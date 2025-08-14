"""Tickets repository (generic schema) for BigQuery.

Provides minimal helpers to read ticket context and write links/resolutions.
Stub client paths become no-ops except they return empty results.
"""
from __future__ import annotations
from typing import Optional, Dict, Any
from .bigquery_client import BigQueryClientBase


class TicketsRepo:
    def __init__(self, client: BigQueryClientBase):
        self.client = client

    def ensure_schema(self) -> None:
        self.client.run_sql_template("ddl_tickets.sql", {})  # type: ignore

    def load_ticket_for_triage(
        self, ticket_id: str, max_comments: int = 5
    ) -> Optional[Dict[str, Any]]:
        rows = self.client.run_sql_template(
            "select_ticket_for_triage.sql",
            {"TICKET_ID": ticket_id, "MAX_COMMENTS": max_comments},
        )
        return rows[0] if rows else None

    def upsert_link(
        self, ticket_id: str, chunk_id: str, relation: str, score: float
    ) -> None:
        self.client.run_sql_template(
            "insert_ticket_links.sql",
            {
                "ticket_id": ticket_id,
                "chunk_id": chunk_id,
                "relation": relation,
                "score": score,
            },
        )

    def upsert_resolution(
        self,
        ticket_id: str,
        playbook_md: str,
        resolution_text: str | None = None,
    ) -> None:
        from datetime import datetime, timezone

        self.client.run_sql_template(
            "insert_resolution.sql",
            {
                "ticket_id": ticket_id,
                "resolved_at": datetime.now(timezone.utc).isoformat(),
                "resolution_text": resolution_text or "",
                "playbook_md": playbook_md,
            },
        )
