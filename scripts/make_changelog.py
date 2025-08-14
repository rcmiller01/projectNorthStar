from __future__ import annotations
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHANGELOG = ROOT / 'CHANGELOG.md'


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()


def last_tag() -> str | None:
    try:
        return run(['git', 'describe', '--tags', '--abbrev=0'])
    except Exception:
        return None


def collect_commits(since: str | None) -> list[str]:
    spec = f"{since}..HEAD" if since else 'HEAD'
    try:
        log = run(['git', 'log', spec, '--pretty=format:* %h %s (%an)'])
    except subprocess.CalledProcessError:
        return []
    return [line for line in log.splitlines() if line.strip()]


GROUPS = [
    ('feat', 'Features'),
    ('fix', 'Fixes'),
    ('docs', 'Docs'),
    ('perf', 'Performance'),
    ('refactor', 'Refactors'),
    ('test', 'Tests'),
    ('chore', 'Chore'),
]


def group_commits(lines: list[str]) -> dict[str, list[str]]:
    buckets: dict[str, list[str]] = {g: [] for g, _ in GROUPS}
    buckets['Other'] = []
    for line in lines:
        matched = False
        for prefix, _ in GROUPS:
            # crude match for prefix in commit subject
            parts = line.split(' ', 3)
            subject = parts[2] if len(parts) > 2 else line
            if re.search(rf"\b{prefix}\b", subject):
                buckets[prefix].append(line)
                matched = True
                break
        if not matched:
            buckets['Other'].append(line)
    return buckets


def render(version: str, buckets: dict[str, list[str]]) -> str:
    today = date.today().isoformat()
    lines = [f"## v{version} — {today}", '']
    title_map = {k: v for k, v in GROUPS}
    title_map['Other'] = 'Other'
    for key, title in title_map.items():
        items = buckets.get(key) or []
        if not items:
            continue
        lines.append(f"### {title}")
        lines.extend(items)
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n\n'


def main(argv=None) -> int:
    if len(sys.argv) < 2:
        print('Usage: python scripts/make_changelog.py <version>')
        return 2
    version = sys.argv[1]
    prev = last_tag()
    commits = collect_commits(prev)
    buckets = group_commits(commits)
    new_section = render(version, buckets)
    old = CHANGELOG.read_text(encoding='utf-8') if CHANGELOG.exists() else ''
    CHANGELOG.write_text(new_section + old, encoding='utf-8')
    print(f'[changelog] updated for v{version} ({len(commits)} commits)')
    return 0


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
