from __future__ import annotations
import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = ROOT / 'pyproject.toml'
MAKE_CHANGELOG = ROOT / 'scripts' / 'make_changelog.py'


def run(cmd: list[str], check: bool = True) -> str:
    proc = subprocess.run(
        cmd,
        check=check,
        text=True,
        capture_output=True,
    )
    return proc.stdout.strip()


def get_current_version() -> str:
    for line in PYPROJECT.read_text(encoding='utf-8').splitlines():
        if line.lower().startswith('version ='):
            return line.split('=')[1].strip().strip('"')
    raise SystemExit('version not found in pyproject.toml')


def bump(version: str, part: str) -> str:
    major, minor, patch = [int(x) for x in version.split('.')]
    if part == 'major':
        major += 1
        minor = 0
        patch = 0
    elif part == 'minor':
        minor += 1
        patch = 0
    elif part == 'patch':
        patch += 1
    else:
        raise SystemExit('part must be major|minor|patch')
    return f"{major}.{minor}.{patch}"


def update_version(new_version: str) -> None:
    lines = PYPROJECT.read_text(encoding='utf-8').splitlines()
    out = []
    for line in lines:
        if line.lower().startswith('version ='):
            out.append(f'version = "{new_version}"')
        else:
            out.append(line)
    PYPROJECT.write_text('\n'.join(out) + '\n', encoding='utf-8')


def git(*args: str) -> str:
    return run(['git', *args])


def ensure_clean() -> None:
    status = git('status', '--porcelain')
    if status.strip():
        raise SystemExit(
            'working tree not clean; commit or stash changes first'
        )


def build_tag(version: str) -> str:
    return f'v{version}'


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description='Release helper')
    p.add_argument(
        '--part',
        choices=['major', 'minor', 'patch'],
        default='patch',
    )
    p.add_argument(
        '--dry-run',
        action='store_true',
        help='Skip file changes & tagging',
    )
    p.add_argument(
        '--version',
        help=(
            'Explicit semantic version (overrides --part and '
            'RELEASE_VERSION env)'
        ),
    )
    args = p.parse_args(argv)

    ensure_clean()
    current = get_current_version()

    forced_env = os.environ.get('RELEASE_VERSION')
    if args.version:
        new_version = args.version.strip()
    elif forced_env:
        new_version = forced_env.strip()
    else:
        new_version = bump(current, args.part)

    print(f'Current version: {current} -> {new_version}')

    dry_env = os.environ.get('DRY_RUN', '') == '1'
    if args.dry_run or dry_env:
        print('[dry-run] skipping file modifications')
        return 0

    update_version(new_version)
    subprocess.check_call([sys.executable, str(MAKE_CHANGELOG), new_version])
    git('add', 'pyproject.toml', 'CHANGELOG.md')
    git('commit', '-m', f'chore(release): v{new_version}')
    tag = build_tag(new_version)
    git('tag', tag)
    print(f'Created tag {tag}. Push with:\n  git push origin main --tags')
    return 0


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
