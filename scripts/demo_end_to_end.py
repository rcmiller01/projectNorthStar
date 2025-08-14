"""End-to-end demo script (Phase 4/8/10).

Steps (live BigQuery required):
 1. Preflight models (scripts/check_bq_resources.py --models-only)
 2. Create dashboard views (idempotent)
 3. Ingest sample data (docs -> chunks -> embeddings refresh)
 4. Freeform triage (writes playbook markdown)
 5. Ticket triage (ensures ticket schema + demo ticket; writes
     links/resolution)
 6. Summarize key telemetry

Exit codes:
 0 success, 1 failure (prints single-line error prefixed with [demo-error])

Environment (must be set): PROJECT_ID, DATASET, LOCATION, BIGQUERY_REAL=1

Flags:
  --no-refresh-loop : disable looping embedding refresh
  --max-comments N  : max comments for ticket triage (default 3)
  --k K             : retrieval top-k (default 5)

Outputs:
  out/demo_freeform.md
  out/demo_ticket.md

Non-PII demo ticket: DEMO-1 with tiny synthetic content.
"""
from __future__ import annotations
import argparse
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

from bq import make_client
from bq.tickets import TicketsRepo

DEMO_TICKET_ID = "DEMO-1"
FREEFORM_TITLE = "500 after password reset"
FREEFORM_BODY = (
    "User hits 500 when resetting password; intermittent after cache clear."
)
TICKET_TITLE = "Intermittent 500 after password reset"
TICKET_BODY = (
    "Small demo ticket body for reproducing password reset 500."  # tiny
)


def die(msg: str) -> None:
    print(f"[demo-error] {msg}")
    sys.exit(1)


def run_cmd(cmd: list[str], label: str) -> None:
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if res.stdout.strip():
            print(res.stdout.strip())
        if res.stderr.strip():  # surface warnings
            print(res.stderr.strip())
    except subprocess.CalledProcessError as exc:  # pragma: no cover
        snippet = (exc.stdout or exc.stderr or "").strip().splitlines()[:3]
        die(f"{label} failed: {' | '.join(snippet)}")


def ensure_env() -> None:
    required = ["PROJECT_ID", "DATASET", "LOCATION", "BIGQUERY_REAL"]
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        die(f"Missing env vars: {','.join(missing)}")
    if os.getenv("BIGQUERY_REAL") != "1":
        die("BIGQUERY_REAL must be 1 for live demo")


def preflight_models() -> None:
    run_cmd(
        [sys.executable, "scripts/check_bq_resources.py", "--models-only"],
        "preflight",
    )


def create_views() -> None:
    run_cmd([sys.executable, "scripts/create_views.py"], "create-views")


def ingest_samples(loop: bool) -> dict:
    args = [
        sys.executable,
        "-m",
        "core.cli",
        "ingest",
        "--path",
        "samples",
        "--type",
        "auto",
        "--max-tokens",
        "512",
    ]
    if loop:
        args.append("--refresh-loop")
    run_cmd(args, "ingest")
    # Stats printed by ingest command; nothing to return here.
    return {}


def freeform_triage(k: int) -> dict:
    out_path = Path("out/demo_freeform.md")
    args = [
        sys.executable,
        "-m",
        "core.cli",
        "triage",
        "--title",
        FREEFORM_TITLE,
        "--body",
        FREEFORM_BODY,
        "--severity",
        "P1",
        "--out",
        str(out_path),
        "--k",
        str(k),
    ]
    run_cmd(args, "freeform-triage")
    return {"out": str(out_path)}


def ensure_demo_ticket(client) -> None:
    repo = TicketsRepo(client)
    repo.ensure_schema()
    # Insert minimal ticket if not present using raw SQL MERGE pattern
    real = getattr(client, "_client", None)
    if real is None:
        return  # stub path: skip
    project = os.getenv("PROJECT_ID")
    dataset = os.getenv("DATASET")
    sql = f"""
    MERGE `{project}.{dataset}.tickets` T
    USING (SELECT '{DEMO_TICKET_ID}' AS ticket_id) S
    ON T.ticket_id = S.ticket_id
    WHEN MATCHED THEN UPDATE SET updated_at = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN INSERT (ticket_id, created_at, severity, title, body)
    VALUES('{DEMO_TICKET_ID}', CURRENT_TIMESTAMP(), 'P1', '{TICKET_TITLE}',
           '{TICKET_BODY}');
    """
    # create a synthetic latest comment
    comment_sql = f"""
        INSERT INTO `{project}.{dataset}.ticket_events`
            (event_id, ticket_id, ts, type, actor, text)
            VALUES(
                CONCAT('evt_demo_',
                     CAST(UNIX_MICROS(CURRENT_TIMESTAMP()) AS STRING)),
                '{DEMO_TICKET_ID}', CURRENT_TIMESTAMP(), 'comment', 'demo',
                'Retry sometimes succeeds.'
            );
    """
    for stmt in [sql, comment_sql]:
        real.query(stmt).result()


def ticket_triage(k: int, max_comments: int, write: bool = True) -> dict:
    out_path = Path("out/demo_ticket.md")
    args = [
        sys.executable,
        "-m",
        "core.cli",
        "triage",
        "--ticket-id",
        DEMO_TICKET_ID,
        "--severity",
        "P1",
        "--out",
        str(out_path),
        "--k",
        str(k),
        "--max-comments",
        str(max_comments),
    ]
    if not write:
        args.append("--no-write")
    run_cmd(args, "ticket-triage")
    return {"out": str(out_path)}


def collect_stats(client) -> dict:
    # Attempt to pull basic counts (best-effort)
    real = getattr(client, "_client", None)
    project = os.getenv("PROJECT_ID")
    dataset = os.getenv("DATASET")
    stats: dict[str, object] = {
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    if real is None:
        return stats

    def q(sql: str) -> int:
        try:
            job = real.query(sql)
            rows = list(job.result())
            return int(rows[0][0]) if rows else 0
        except Exception:
            return 0
    stats["ticket_links"] = q(
        ("SELECT COUNT(*) FROM `{}.{}`.ticket_chunk_links "
         "WHERE ticket_id='{}'").format(project, dataset, DEMO_TICKET_ID)
    )
    stats["resolutions"] = q(
        ("SELECT COUNT(*) FROM `{}.{}`.resolutions "
         "WHERE ticket_id='{}'").format(project, dataset, DEMO_TICKET_ID)
    )
    return stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run full demo pipeline")
    parser.add_argument("--no-refresh-loop", action="store_true")
    parser.add_argument("--max-comments", type=int, default=3)
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args(argv)

    ensure_env()
    client = make_client()

    try:
        preflight_models()
        create_views()
        ingest_samples(loop=not args.no_refresh_loop)
        freeform_triage(k=args.k)
        ensure_demo_ticket(client)
        ticket_triage(k=args.k, max_comments=args.max_comments, write=True)
        stats = collect_stats(client)
    except SystemExit:
        raise
    except Exception as exc:  # pragma: no cover
        die(str(exc))

    print(
        (
            "[demo-summary] ticket_links={links} resolutions={resolutions} "
            "k={k}"
        ).format(
            links=stats.get("ticket_links", 0),
            resolutions=stats.get("resolutions", 0),
            k=args.k,
        )
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
