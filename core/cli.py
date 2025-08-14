"""CLI entrypoints for NorthStar Phase 1.

Usage:
    python -m core.cli triage \
        --title "Issue title" \
        --body "Long body" \
        --out out/playbook.md
"""
from __future__ import annotations
import argparse

from bq import make_client
from ingest import extract_text, parse_log, to_chunks
from bq.load import upsert_documents, upsert_chunks
from bq.refresh import refresh_embeddings
from pathlib import Path
from core.orchestrator import Orchestrator


SEVERITY_MAP = {
    "p0": "P0",
    "p1": "P1",
    "p2": "P2",
    "p3": "P3",
    "high": "High",
    "medium": "Medium",
    "low": "Low",
    "unknown": "Unknown",
}


def _norm_severity(raw: str | None) -> str:
    if not raw:
        return "Unknown"
    return SEVERITY_MAP.get(raw.lower(), "Unknown")


def cmd_triage(args: argparse.Namespace) -> int:
    client = make_client()
    orch = Orchestrator(client)
    ticket: dict[str, str] = {
        "title": args.title or "",
        "body": args.body or "",
    }
    sev = _norm_severity(getattr(args, "severity", None))
    ticket["severity"] = sev
    result = orch.triage(ticket, k=args.k)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(result["draft_md"], encoding="utf-8")
    print(f"Playbook written: {out_path} (ok={result['draft_ok']})")
    stats = result.get("stats", {})
    violations = 0 if result.get("draft_ok") else 1
    print(
        (
            "severity={sev} score={ok} violations={violations} "
            "snippets={k} min_dist={d}"
        ).format(
            sev=sev,
            ok=stats.get("ok"),
            violations=violations,
            k=stats.get("k"),
            d=stats.get("min_distance"),
        )
    )
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
        "--severity",
        help=(
            "Severity classification (P0,P1,P2,P3,High,Medium,Low,Unknown). "
            "Case-insensitive; defaults Unknown."
        ),
    )
    t.add_argument(
        "--out",
        default="out/playbook.md",
        help="Output markdown path",
    )
    t.set_defaults(func=cmd_triage)

    ing = sub.add_parser("ingest", help="Ingest OCR/log files and embed")
    ing.add_argument("--path", required=True, help="Root path to scan")
    ing.add_argument(
        "--type",
        default="auto",
        choices=["auto", "pdf", "image", "log"],
        help="Force a type or auto-detect by extension",
    )
    ing.add_argument(
        "--max-tokens", type=int, default=512, help="Chunk max tokens"
    )
    ing.add_argument(
        "--refresh-loop",
        action="store_true",
        help="Loop embedding refresh until no new rows inserted",
    )
    ing.set_defaults(func=cmd_ingest)
    return p


def _iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob("*"):
        if p.is_file():
            files.append(p)
    return files


def cmd_ingest(args: argparse.Namespace) -> int:
    client = make_client()
    root = Path(args.path)
    if not root.exists():
        print(f"Path not found: {root}")
        return 1
    all_docs: list[dict] = []
    all_chunks: list[dict] = []
    for f in _iter_files(root):
        ext = f.suffix.lower()
        recs = []
        if args.type == "log" or (
            args.type == "auto" and ext in {".log", ".txt"}
        ):
            recs = parse_log(str(f))
        elif args.type in {"pdf", "image"}:
            if args.type == "pdf" and ext == ".pdf":
                recs = extract_text(str(f))
            elif args.type == "image" and ext in {".png", ".jpg", ".jpeg"}:
                recs = extract_text(str(f))
        elif args.type == "auto" and ext in {".pdf", ".png", ".jpg", ".jpeg"}:
            recs = extract_text(str(f))
        if not recs:
            continue
        # document abstraction: one per file (first record doc_id)
        doc_meta = {"filename": f.name, "records": len(recs)}
        all_docs.append(
            {
                "doc_id": recs[0]["doc_id"],
                "type": recs[0]["type"],
                "uri": recs[0]["uri"],
                "meta": doc_meta,
            }
        )
        chunks = to_chunks(recs, max_tokens=args.max_tokens)
        all_chunks.extend(
            {
                "chunk_id": c["chunk_id"],
                "doc_id": c["doc_id"],
                "text": c["text"],
                "meta": c["meta"],
            }
            for c in chunks
        )
    docs_effective = upsert_documents(client, all_docs)
    chunks_effective = upsert_chunks(client, all_chunks)
    emb_stats = refresh_embeddings(client, loop=getattr(args, "refresh_loop", False))
    msg = (
        "DocsEff:{d} ChunksEff:{c} Embeddings(batches={b} total={t} last={lb}) "
        "(total_docs={td} total_chunks={tc})"
    ).format(
        d=docs_effective,
        c=chunks_effective,
        b=emb_stats.get("batches"),
        t=emb_stats.get("total_inserted"),
        lb=emb_stats.get("last_batch"),
        td=len(all_docs),
        tc=len(all_chunks),
    )
    print(msg)
    return 0


def main(argv: list[str] | None = None) -> int:  # pragma: no cover
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
