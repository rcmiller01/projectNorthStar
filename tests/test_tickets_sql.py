from pathlib import Path

SQL_DIR = Path("sql")


def _read(name: str) -> str:
    return (SQL_DIR / name).read_text(encoding="utf-8")


def test_ddl_tickets_has_creates():
    body = _read("ddl_tickets.sql")
    creates = [
        line
        for line in body.splitlines()
        if line.strip().upper().startswith("CREATE TABLE IF NOT EXISTS")
    ]
    assert len(creates) == 5, (
        f"expected 5 CREATE TABLE IF NOT EXISTS, got {len(creates)}"
    )


def test_select_ticket_for_triage_references_tables():
    body = _read("select_ticket_for_triage.sql")
    assert "tickets`" in body
    assert "ticket_events`" in body
    assert "@ticket_id" in body


def test_merge_templates():
    links = _read("insert_ticket_links.sql")
    res = _read("insert_resolution.sql")
    assert "MERGE" in links.upper()
    assert "MERGE" in res.upper()
