"""Ticket Plan Mode router.

Emits clarifying questions and a plan header for a ticket.
"""
from __future__ import annotations
from typing import Dict, List

STANDARD_QUESTIONS = [
    "What environment (prod/staging/local)?",
    "Recent changes or deployments?",
    "Exact error code / stack trace snippet?",
    "User impact & scope (single vs all)?",
    "Any mitigations already tried?",
    "Version / build or dependency changes?",
]


def plan_mode(ticket: Dict[str, str]) -> Dict[str, object]:
    """Generate clarifying questions and a plan header for the ticket.

    Parameters
    ----------
    ticket: dict with optional keys 'title', 'body'

    Returns
    -------
    dict with keys: clarifying_questions, plan_header, next_action
    """
    title = (ticket.get("title") or "").strip()
    body = (ticket.get("body") or "").strip()
    summary = title if title else body[:120]
    assumptions: List[str] = []
    if not title:
        assumptions.append("Title missing; summary derived from body snippet.")
    plan_header = {
        "summary": summary,
        "assumptions": assumptions,
    }
    return {
        "clarifying_questions": STANDARD_QUESTIONS.copy(),
        "plan_header": plan_header,
        "next_action": (
            "Run retrieval with vector search (k<=8) and return citations."
        ),
    }

# Reflection:
# Plan aligned with spec; no deviations.
# Next improvement: incorporate prior similar tickets cache.
