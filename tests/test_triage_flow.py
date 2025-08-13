"""Acceptance test for Phase 1 triage orchestrator."""
from __future__ import annotations

from core.orchestrator import Orchestrator
from bq import make_client


def test_triage_basic() -> None:
    client = make_client()  # stub by default
    orch = Orchestrator(client)
    ticket = {
        "title": "Login fails intermittently",
        "body": "Users report 500",
    }
    result = orch.triage(ticket, k=3)
    assert result["plan"]["clarifying_questions"], "Questions missing"
    assert len(result["snippets"]) == 1  # stub returns 1 row
    md = result["draft_md"]
    assert "# Agent Playbook" in md
    assert result["draft_ok"], result["verify_msg"]
