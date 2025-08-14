"""BigQuery resource preflight: dataset, tables, models.

Adds --models-only fast path to just verify remote models referenced by
env vars BQ_EMBED_MODEL / BQ_GEN_MODEL.
"""
from __future__ import annotations
import os
import sys
import argparse
from _bq_utils import model_exists, dataset_location

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

 
# (local model_exists removed; using shared helper)

 
def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Preflight BigQuery resources (dataset, tables, models)."
    )
    parser.add_argument(
        "--models-only",
        action="store_true",
        help="Only verify remote models (skip dataset/table checks)",
    )
    args = parser.parse_args(argv)

    client = bigquery.Client(project=PROJECT, location=LOCATION)
    # Region / location info
    bq_loc = dataset_location(client, PROJECT, DATASET)
    vertex_region = os.getenv("VERTEX_REGION", "")
    if bq_loc:
        print(f"ℹ️  BigQuery dataset location: {bq_loc}")
    else:
        print(
            "ℹ️  Could not determine dataset location (ensure dataset exists)"
        )
    if vertex_region:
        print(f"ℹ️  Vertex region (VERTEX_REGION): {vertex_region}")
    # Heuristic warnings (non-fatal)
    if bq_loc and vertex_region:
        u = bq_loc.upper()
        if u == "US" and not vertex_region.startswith("us-"):
            print(
                "⚠️  Region mismatch: dataset in US multi-region vs "
                "Vertex region"
            )
        elif u == "EU" and not vertex_region.startswith(("europe-", "eu-")):
            print(
                "⚠️  Region mismatch: dataset in EU multi-region vs "
                "Vertex region"
            )

    def check_models() -> int:
        missing_ct = 0
        if EMBED_MDL:
            if model_exists(client, EMBED_MDL):
                ok(f"embed model OK: {EMBED_MDL}")
            else:
                print(f"❌ embed model missing: {EMBED_MDL}")
                missing_ct += 1
        else:
            print("ℹ️  BQ_EMBED_MODEL not set; skipping embed model check")
        if GEN_MDL:
            if model_exists(client, GEN_MDL):
                ok(f"text model OK: {GEN_MDL}")
            else:
                print(f"❌ text model missing: {GEN_MDL}")
                missing_ct += 1
        else:
            print("ℹ️  BQ_GEN_MODEL not set; skipping text model check")
        return missing_ct

    if args.models_only:
        missing = check_models()
        if missing:
            sys.exit(1)
        print("🎉 Models preflight passed.")
        return

    # Full preflight (dataset + tables + models)
    try:
        client.get_dataset(f"{PROJECT}.{DATASET}")
        ok(f"dataset {PROJECT}.{DATASET} exists")
    except Exception:
        die(
            f"dataset {PROJECT}.{DATASET} not found (create it or run Phase-0 "
            "notebook first)"
        )

    needed = {"demo_texts", "demo_texts_emb"}
    existing = {t.table_id for t in client.list_tables(f"{PROJECT}.{DATASET}")}
    missing_tables = needed - existing
    if missing_tables:
        die(
            "missing tables in {ds}: {m}".format(
                ds=f"{PROJECT}.{DATASET}", m=", ".join(sorted(missing_tables))
            )
        )
    ok("tables demo_texts & demo_texts_emb exist")

    if check_models():
        sys.exit(1)

    print("🎉 BigQuery preflight passed.")


if __name__ == "__main__":  # pragma: no cover
    main()
