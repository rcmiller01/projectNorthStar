"""Secret sweep script.

Scans repository for potential secrets using regex & simple entropy heuristics.
High-signal findings trigger non-zero exit (unless allowlisted).

Usage:
  python scripts/secret_sweep.py [--fail-on=MED]

Allowlist:
  secrets_allowlist.txt (optional). Lines may be:
    # comment
    regex:<pattern>
    path:<relative_path>

Exit codes:
  0: no disallowed secrets
  1: high severity finding(s) (or >= threshold)
  2: internal error
"""
from __future__ import annotations
import argparse
import json
import math
import re
import os
from pathlib import Path
from typing import Iterable, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
ALLOWLIST_FILE = ROOT / "secrets_allowlist.txt"
DEFAULT_SKIP = {
    ".git", ".venv", "venv", "env", "__pycache__", ".pytest_cache",
    ".mypy_cache", "node_modules", ".ruff_cache", ".idea", ".vscode",
    ".DS_Store", "out", "metrics", "build", "dist", "docs"
}
extra = os.environ.get("SECRETS_SKIP_DIRS", "")
SKIP_DIRS = DEFAULT_SKIP | {p.strip() for p in extra.split(',') if p.strip()}
SKIP_FILES = {"docs/dashboard.png"}
SCAN_OUT = ROOT / 'secret-scan.txt'

RULES: List[Tuple[str, str, str]] = [
    ("HIGH", "AWS Access Key", r"AKIA[0-9A-Z]{16}"),
    ("HIGH", "AWS Temp Access Key", r"ASIA[0-9A-Z]{16}"),
    ("HIGH", "GitHub PAT", r"ghp_[0-9A-Za-z]{36}"),
    ("HIGH", "OpenAI Key", r"sk-[A-Za-z0-9]{32,}"),
    ("HIGH", "Slack Token", r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    (
        "HIGH",
        "PEM Private Key",
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    ),
    ("HIGH", "GCP Service Account", r'"type"\s*:\s*"service_account"'),
    ("MED", "Bearer/JWT", r"Bearer [A-Za-z0-9_\-\.=]{20,}"),
    (
        "MED",
        "Generic JWT",
        r"eyJ[A-Za-z0-9_-]+?\.eyJ[A-Za-z0-9_-]+?\.[A-Za-z0-9_-]{10,}",
    ),
    (
        "MED",
        "Azure Key",
        r"[Aa][Zz][Uu][Rr][Ee].{0,20}[Kk][Ee][Yy].{0,5}[:=].{10,}",
    ),
    ("MED", ".env assignment", r"^[A-Z0-9_]{3,} ?= ?[^\n]{8,}$"),
]

ENTROPY_THRESHOLD = 4.2  # shannon bits/char for medium length tokens
ENTROPY_MIN_LEN = 20


def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    freq = {ch: s.count(ch) for ch in set(s)}
    length = len(s)
    return -sum((c/length) * math.log2(c/length) for c in freq.values())


def load_allowlist():
    regexes: List[re.Pattern] = []
    paths: set[str] = set()
    if not ALLOWLIST_FILE.exists():
        return regexes, paths
    for line in ALLOWLIST_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('regex:'):
            pat = line[len('regex:'):].strip()
            try:
                regexes.append(re.compile(pat))
            except re.error:
                pass
        elif line.startswith('path:'):
            p = line[len('path:'):].strip()
            paths.add(p)
    return regexes, paths


def iter_files(start: Path = ROOT) -> Iterable[Path]:
    for root, dirs, files in os.walk(start):
        # prune skip dirs in-place
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            p = Path(root) / f
            rel = p.relative_to(start).as_posix()
            if rel in SKIP_FILES:
                continue
            if p.suffix.lower() in {
                '.png', '.jpg', '.jpeg', '.gif', '.ico', '.exe', '.dll'
            }:
                continue
            yield p


def scan_file(path: Path) -> List[dict]:
    out: List[dict] = []
    try:
        text = path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return out
    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        for sev, name, pattern in RULES:
            if re.search(pattern, line):
                out.append({
                    'severity': sev,
                    'rule': name,
                    'file': str(path.relative_to(ROOT)),
                    'line': i,
                    'snippet': line.strip()[:160]
                })
        tokens = re.findall(r"([A-Za-z0-9+/=_-]{20,})", line)
        for t in tokens:
            if (
                len(t) >= ENTROPY_MIN_LEN
                and shannon_entropy(t) >= ENTROPY_THRESHOLD
            ):
                out.append({
                    'severity': 'MED',
                    'rule': 'High-entropy token',
                    'file': str(path.relative_to(ROOT)),
                    'line': i,
                    'snippet': t[:160]
                })
    return out


def apply_allowlist(findings: List[dict], regexes, paths) -> List[dict]:
    filtered = []
    for f in findings:
        if f['file'] in paths:
            continue
        if any(r.search(f['snippet']) for r in regexes):
            continue
        filtered.append(f)
    return filtered


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--fail-on', choices=['HIGH', 'MED'], default='HIGH')
    ap.add_argument('--json', action='store_true', help='Output JSON')
    args = ap.parse_args(argv)
    regex_allow, path_allow = load_allowlist()
    all_findings: List[dict] = []
    for file_path in iter_files():
        all_findings.extend(scan_file(file_path))
    findings = apply_allowlist(all_findings, regex_allow, path_allow)
    output_lines = []
    if not findings:
        output_lines.append('[secret-sweep] no findings')
    else:
        header = 'severity | file:line | rule | snippet'
        output_lines.append(header)
        output_lines.append('-' * len(header))
        for finding in findings:
            seg1 = (
                f"{finding['severity']:6} | "
                f"{finding['file']}:{finding['line']} |"
            )
            seg2 = f" {finding['rule']} | {finding['snippet']}"
            output_lines.append(seg1 + seg2)
    # stdout formatting
    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        print('\n'.join(output_lines))
    # always write plain text table for CI artifact
    try:
        SCAN_OUT.write_text('\n'.join(output_lines) + '\n', encoding='utf-8')
    except Exception:
        pass
    sev_order = {'HIGH': 2, 'MED': 1, 'LOW': 0}
    threshold = sev_order[args.fail_on]
    worst = max((sev_order[f['severity']] for f in findings), default=-1)
    return 1 if worst >= threshold and findings else 0


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
