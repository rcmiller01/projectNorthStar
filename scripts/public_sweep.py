"""Public sweep script.

Checks for large files, notebook outputs, stray credentials, internal URLs.

Exit codes:
 0: clean or only warnings
 1: blocking issue (large file, credential file)
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_FILE_MB = 25
ALLOW_LARGE = {"docs/dashboard.png"}
BLOCK_EXT = {".pem", ".key", ".p8", ".sqlite"}
CRED_FILENAMES = {"service_account.json", ".env"}
INTERNAL_URL_PAT = re.compile(
    r"https?://(localhost|127\.0\.0\.1|internal|corp)", re.I
)


def human_size(b: int) -> str:
    return f"{b/1024/1024:.2f}MB"


def list_tracked_files():
    # fallback to walking if git absent
    try:
        import subprocess  # local import
        out = subprocess.check_output(["git", "ls-files"], text=True)
        return [
            ROOT / line.strip()
            for line in out.splitlines()
            if line.strip()
        ]
    except Exception:
        return [p for p in ROOT.rglob('*') if p.is_file()]


def scan_large(tracked):
    problems = []
    for p in tracked:
        rel = p.relative_to(ROOT).as_posix()
        if rel in ALLOW_LARGE:
            continue
        size = p.stat().st_size
        if size > MAX_FILE_MB * 1024 * 1024:
            problems.append((rel, size))
    return problems


def scan_notebooks(tracked):
    """Return notebooks that appear to contain sizable outputs.

    Heuristics: very long text lines or any image/* data blobs.
    """
    try:
        import nbformat  # type: ignore
    except Exception:
        return []
    suspects = []
    for p in tracked:
        if p.suffix != '.ipynb':
            continue
        try:
            nb = nbformat.read(p.open('r', encoding='utf-8'), as_version=4)
        except Exception:
            continue
        for cell in nb.get('cells', []):
            if cell.get('cell_type') != 'code':
                continue
            for out in cell.get('outputs', []):
                if 'text' in out and any(
                    len(line) > 2000 for line in out['text']
                ):
                    suspects.append(p.relative_to(ROOT).as_posix())
                    break
                data = out.get('data', {})
                if any(k.startswith('image/') for k in data.keys()):
                    suspects.append(p.relative_to(ROOT).as_posix())
                    break
    return sorted(set(suspects))


def scan_creds(tracked):
    hits = []
    for p in tracked:
        rel = p.relative_to(ROOT).as_posix()
        if p.name in CRED_FILENAMES or p.suffix in BLOCK_EXT:
            hits.append(rel)
    return hits


def scan_internal_urls(tracked):
    warns = []
    for p in tracked:
        if p.suffix not in {'.md', '.ipynb', '.py'}:
            continue
        try:
            text = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        if INTERNAL_URL_PAT.search(text):
            warns.append(p.relative_to(ROOT).as_posix())
    return warns


def main():
    tracked = list_tracked_files()
    large = scan_large(tracked)
    noisy_nb = scan_notebooks(tracked)
    creds = scan_creds(tracked)
    internal = scan_internal_urls(tracked)

    if large:
        print('[public-sweep] LARGE files:')
        for rel, size in large:
            print(f"  {rel} {human_size(size)} > {MAX_FILE_MB}MB")
    if noisy_nb:
        print('[public-sweep] Notebooks with outputs (consider clearing):')
        for rel in noisy_nb:
            print(f"  {rel}")
    if creds:
        print('[public-sweep] Credential-like files:')
        for rel in creds:
            print(f"  {rel}")
    if internal:
        print('[public-sweep] Internal/private URLs (warn):')
        for rel in internal:
            print(f"  {rel}")

    fail = bool(large or creds)
    if fail:
        print('[public-sweep] FAIL: remove or allowlist offending files.')
    else:
        print('[public-sweep] OK')
    return 1 if fail else 0


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
