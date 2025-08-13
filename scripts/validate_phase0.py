"""Phase-0 BigQuery AI validation script.

Checks:
1) Embeddings table exists with non-empty ARRAY<FLOAT64> 'embedding'.
2) VECTOR_SEARCH returns >=1 row with distance.
3) ML.GENERATE_TEXT returns parseable JSON with {severity, component}.
"""
from __future__ import annotations
import os, json, sys
from typing import Any, Dict

try:
    from google.cloud import bigquery  # type: ignore
except Exception as exc:  # pragma: no cover
    print("google-cloud-bigquery not installed. Install extras: pip install -e .[bigquery]")
    raise

PROJECT   = os.getenv("PROJECT_ID", "bq_project_northstar")
DATASET   = os.getenv("DATASET", "demo_ai")
LOCATION  = os.getenv("LOCATION", "US")
EMBED_TBL = f"`{PROJECT}.{DATASET}.demo_texts_emb`"
EMBED_MDL = os.getenv("BQ_EMBED_MODEL", "text-embedding-004")
GEN_MODEL = os.getenv("BQ_GEN_MODEL", "gemini-1.5-pro")


def run(sql: str, params: Dict[str, Any] | None = None):
    client = bigquery.Client(project=PROJECT, location=LOCATION)
    job = client.query(sql, job_config=bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter(k, "STRING", v) for k, v in (params or {}).items()
    ]))
    return list(job.result())


def assert_true(cond: bool, msg: str):
    if not cond:
        print(f"❌ {msg}")
        sys.exit(1)
    print(f"✅ {msg}")


def main():
    # 1) Embedding shape & rows
    rows = run(f"SELECT ARRAY_LENGTH(embedding) AS L FROM {EMBED_TBL} LIMIT 5")
    assert_true(len(rows) > 0, "embedded table has rows")
        assert_true(all(r["L"] and r["L"] > 0 for r in rows), "embedding vectors have length > 0")

        # 2) Vector search sanity (embed the query inline using same model)
        vs_sql = f"""
        DECLARE q STRING DEFAULT @q;
        SELECT id, text, distance
        FROM ML.VECTOR_SEARCH(
            TABLE {EMBED_TBL},
            (SELECT ML.GENERATE_EMBEDDING(MODEL `{PROJECT}.{LOCATION}.{EMBED_MDL}`) AS embedding FROM UNNEST([q])),
            top_k => 3
        )
        """
    vs = run(vs_sql, {"q": "login 500 after password reset"})
    assert_true(len(vs) >= 1 and "distance" in vs[0], "vector search returns >=1 row w/ distance")

        # 3) Text gen JSON fields
        tg_sql = f"""
        SELECT ML.GENERATE_TEXT(
            MODEL `{PROJECT}.{LOCATION}.{GEN_MODEL}`,
            PROMPT => 'Return JSON with fields severity and component for: "Login 500 after reset".'
        ) AS out
        """
    tg = run(tg_sql)
    parsed = json.loads(tg[0]["out"]) if tg and tg[0]["out"] else {}
    assert_true(isinstance(parsed, dict) and {"severity", "component"} <= parsed.keys(),
                "text-gen JSON has {severity, component}")

    print("🎉 Phase-0 validation passed.")


if __name__ == "__main__":  # pragma: no cover
    main()
