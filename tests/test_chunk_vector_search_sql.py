import re
from pathlib import Path

SQL_PATH = Path("sql/chunk_vector_search.sql")


def test_chunk_vector_search_sql_variables_present():
    sql = SQL_PATH.read_text(encoding="utf-8")
    # Ensure required variables are referenced
    required = [
        "${PROJECT_ID}",
        "${DATASET}",
        "${TOP_K}",
        "${QUERY_TEXT}",
        "${EMBED_MODEL}",
    ]
    for var in required:
        assert var in sql
    # Ensure meta selected
    # Allow for newlines/spaces between SELECT and columns
    pattern = r"SELECT\s+vs\.chunk_id[\s,\S]*c\.meta"
    assert re.search(pattern, sql, re.IGNORECASE | re.DOTALL)


def test_chunk_vector_search_has_type_filter_clause():
    sql = SQL_PATH.read_text(encoding="utf-8")
    assert "JSON_VALUE(c.meta, '$.type')" in sql
    assert "TYPE_ARRAY" in sql or "ARRAY_LENGTH(${TYPE_ARRAY})" in sql
