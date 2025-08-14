import pathlib

SQL_DIR = pathlib.Path("sql")


def _read(name: str) -> str:
    return (SQL_DIR / name).read_text(encoding="utf-8")


def test_common_issues_contains_expected_clauses():
    src = _read("views_common_issues.sql")
    assert "CREATE OR REPLACE VIEW" in src
    assert "COUNT(*)" in src or "COUNT (" in src
    assert "LOWER(" in src or "lower(" in src
    assert "REGEXP_REPLACE" in src


def test_by_severity_contains_expected_clauses():
    src = _read("views_by_severity.sql")
    assert "CREATE OR REPLACE VIEW" in src
    assert "DATE_TRUNC" in src
    assert "CASE" in src
    assert "severity" in src.lower()


def test_duplicates_contains_expected_clauses():
    src = _read("views_duplicates.sql")
    assert "CREATE OR REPLACE VIEW" in src
    assert "ML.VECTOR_SEARCH" in src
    assert "DECLARE distance_thresh" in src  # comment form acceptable
    assert "JOIN `${PROJECT_ID}.${DATASET}.chunks`" in src
