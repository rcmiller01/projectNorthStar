from pathlib import Path
import verifier


def test_verify_sql_directory() -> None:
    sql_dir = Path("sql")
    assert verifier.verify_sql_directory(sql_dir) is True
