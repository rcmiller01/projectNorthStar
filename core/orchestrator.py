"""Orchestrator for triage flow: plan -> retrieve -> draft -> verify.
"""
from __future__ import annotations
from typing import Any, Dict, cast
from experts import router, kb_writer
from verify import kb_verifier
from retrieval.hybrid import vector_search
from bq.bigquery_client import BigQueryClientBase


class Orchestrator:
    """Coordinates the triage sequence."""

    def __init__(self, bq_client: BigQueryClientBase) -> None:
        self._bq = bq_client

    def triage(self, ticket: Dict[str, str], k: int = 5) -> Dict[str, Any]:
        """Execute full loop, returning structured result dict."""
        plan = router.plan_mode(ticket)
        query_text = ticket.get("title") or ticket.get("body") or ""
        snippets = vector_search(self._bq, query_text=query_text, k=k)
        plan_header = cast(Dict[str, Any], plan["plan_header"])
        md = kb_writer.render_agent_playbook(plan_header, snippets)
        ok, msg = kb_verifier.verify_agent_playbook(md)
        # basic telemetry for later dashboarding
        stats = {
            "k": len(snippets),
            "min_distance": min(
                (s.get("distance", 1.0) for s in snippets), default=1.0
            ),
            "ok": ok,
        }
        print(f"[triage_stats] {stats}")
        return {
            "plan": plan,
            "snippets": snippets,
            "draft_md": md,
            "draft_ok": ok,
            "verify_msg": msg,
            "stats": stats,
        }

# Reflection:
# Straight mapping from spec.
# Next improvement: feed clarifier answers into retrieval.
