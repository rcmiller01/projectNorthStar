"""Static checks over SQL templates for Phase 0.

Ensures required ML.* constructs present and parameter placeholders exist.
"""
from __future__ import annotations
from pathlib import Path

SQL_DIR = Path("sql")
REQUIRED = ["ML.GENERATE_EMBEDDING", "ML.VECTOR_SEARCH"]
OPTIONAL = ["ML.GENERATE_TEXT"]


def read_sql(name: str) -> str:
    return (SQL_DIR / name).read_text(encoding="utf-8")


def test_required_terms_present() -> None:
    body = "\n".join(
        p.read_text(encoding="utf-8") for p in SQL_DIR.glob("*.sql")
    )
    for term in REQUIRED:
        assert term in body, f"Missing term {term} in SQL templates"


def test_embeds_table_name() -> None:
    embeddings_sql = read_sql("embeddings.sql")
    assert "demo_texts_emb" in embeddings_sql


def test_vector_search_query_embed() -> None:
    vs_sql = read_sql("vector_search.sql")
    assert "ML.GENERATE_EMBEDDING" in vs_sql
    assert "top_k =>" in vs_sql


def test_optional_text_gen_detectable() -> None:
    gen_sql = read_sql("generate_text.sql")
    assert "ML.GENERATE_TEXT" in gen_sql
