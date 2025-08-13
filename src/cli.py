"""CLI entrypoint for contest scaffold."""
from __future__ import annotations
import argparse
from pathlib import Path
from bigquery_client import BigQueryClient
import retrieval as retrieval_mod
import verifier as verifier_mod


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("northstar-cli")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_retr = sub.add_parser("retrieve", help="Run retrieval for a query")
    p_retr.add_argument("query", type=str)
    p_retr.add_argument("--top-k", type=int, default=5)

    p_ver = sub.add_parser(
        "verify-sql", help="Verify SQL templates contain AI usage"
    )
    p_ver.add_argument("path", type=Path, default=Path("sql"))

    return p


def cmd_retrieve(args: argparse.Namespace) -> None:
    client = BigQueryClient(project_id="demo", dry_run=True)
    results = retrieval_mod.retrieve(client, args.query, top_k=args.top_k)
    for r in results:
        print(r)


def cmd_verify_sql(args: argparse.Namespace) -> None:
    ok = verifier_mod.verify_sql_directory(args.path)
    if ok:
        print("OK: required BigQuery AI constructs present")
    else:
        print("FAIL: missing required constructs")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.cmd == "retrieve":
        cmd_retrieve(args)
    elif args.cmd == "verify-sql":
        cmd_verify_sql(args)
    else:  # pragma: no cover
        parser.error("Unknown command")


if __name__ == "__main__":  # pragma: no cover
    main()
