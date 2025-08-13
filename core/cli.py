"""CLI entrypoints for NorthStar Phase 1.

Usage:
    python -m core.cli triage \
        --title "Issue title" \
        --body "Long body" \
        --out out/playbook.md
"""
from __future__ import annotations
import argparse
from pathlib import Path

from bq import make_client
from core.orchestrator import Orchestrator


def cmd_triage(args: argparse.Namespace) -> int:
    client = make_client()
    orch = Orchestrator(client)
    ticket: dict[str, str] = {
        "title": args.title or "",
        "body": args.body or "",
    }
    result = orch.triage(ticket, k=args.k)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(result["draft_md"], encoding="utf-8")
    print(f"Playbook written: {out_path} (ok={result['draft_ok']})")
    if not result["draft_ok"]:
        print(f"Verification: {result['verify_msg']}")
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="northstar")
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("triage", help="Run plan->retrieve->draft->verify loop")
    t.add_argument("--title", help="Ticket title", required=False)
    t.add_argument("--body", help="Ticket body", required=False)
    t.add_argument("--k", type=int, default=5, help="Top K snippets")
    t.add_argument(
        "--out",
        default="out/playbook.md",
        help="Output markdown path",
    )
    t.set_defaults(func=cmd_triage)
    return p


def main(argv: list[str] | None = None) -> int:  # pragma: no cover
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
