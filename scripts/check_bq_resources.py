"""BigQuery resource preflight: dataset, tables, models."""
from __future__ import annotations
import os
import sys

try:
    from google.cloud import bigquery  # type: ignore
except Exception:  # pragma: no cover
    print(
        "google-cloud-bigquery not installed. Install with: "
        "pip install -e .[bigquery]"
    )
    raise

PROJECT = os.getenv("PROJECT_ID", "bq_project_northstar")
DATASET = os.getenv("DATASET", "demo_ai")
LOCATION = os.getenv("LOCATION", "US")
EMBED_MDL = os.getenv(
    "BQ_EMBED_MODEL", ""
)  # fully-qualified e.g. proj.dataset.embed_model
GEN_MDL = os.getenv(
    "BQ_GEN_MODEL", ""
)  # fully-qualified e.g. proj.dataset.gemini_model

 
def die(msg: str) -> None:
    print(f"❌ {msg}")
    sys.exit(1)

 
def ok(msg: str) -> None:
    print(f"✅ {msg}")

 
def model_exists(client: "bigquery.Client", fqid: str) -> bool:
    if not fqid or fqid.count(".") != 2:
        return False
    proj, ds, name = fqid.split(".")
    sql = (
        "SELECT model_name FROM `{proj}.{ds}.INFORMATION_SCHEMA.MODELS` "
        "WHERE model_name=@name"
    ).format(proj=proj, ds=ds)
    job = client.query(
        sql,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("name", "STRING", name)
            ]
        ),
    )
    rows = list(job.result())
    return len(rows) > 0

 
def main() -> None:
    client = bigquery.Client(project=PROJECT, location=LOCATION)

    # Dataset
    try:
        client.get_dataset(f"{PROJECT}.{DATASET}")
        ok(f"dataset {PROJECT}.{DATASET} exists")
    except Exception:
        die(
            f"dataset {PROJECT}.{DATASET} not found (create it or run Phase-0 "
            "notebook first)"
        )

    # Tables
    needed = {"demo_texts", "demo_texts_emb"}
    existing = {t.table_id for t in client.list_tables(f"{PROJECT}.{DATASET}")}
    missing = needed - existing
    if missing:
        die(
            "missing tables in {ds}: {m}".format(
                ds=f"{PROJECT}.{DATASET}", m=", ".join(sorted(missing))
            )
        )
    ok("tables demo_texts & demo_texts_emb exist")

    # Models
    if EMBED_MDL:
        ok(f"embed model OK: {EMBED_MDL}") if model_exists(
            client, EMBED_MDL
        ) else die(f"embed model not found: {EMBED_MDL}")
    else:
        print("ℹ️  BQ_EMBED_MODEL not set; skipping embed model check")
    if GEN_MDL:
        ok(f"text model OK: {GEN_MDL}") if model_exists(
            client, GEN_MDL
        ) else die(f"text model not found: {GEN_MDL}")
    else:
        print("ℹ️  BQ_GEN_MODEL not set; skipping text model check")

    print("🎉 BigQuery preflight passed.")


if __name__ == "__main__":  # pragma: no cover
    main()
