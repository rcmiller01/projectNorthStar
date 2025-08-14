"""Orchestrator for triage flow: plan -> retrieve -> draft -> verify.
"""
from __future__ import annotations
from typing import Any, Dict, cast
from experts import router, kb_writer
from verify import kb_verifier
from retrieval.hybrid import vector_search
from bq.tickets import TicketsRepo
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
        sev = ticket.get("severity")
        if sev:
            plan_header.setdefault("assumptions", []).append(
                f"Severity: {sev}"
            )
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

    def triage_ticket(
        self,
        ticket_id: str,
        max_comments: int = 5,
        severity: str = "Unknown",
        k: int = 5,
        write: bool = True,
    ) -> Dict[str, Any]:
        repo = TicketsRepo(self._bq)
        # load ticket (may be None)
        record = repo.load_ticket_for_triage(ticket_id, max_comments)
        if not record:
            # fabricate minimal placeholder
            ticket = {
                "title": f"Ticket {ticket_id} (not found)",
                "body": "",
                "severity": severity,
            }
        else:
            # build composite body including comments if present
            comments = record.get("recent_comments") or ""
            body = record.get("body") or ""
            composite_body = body
            if comments:
                composite_body = (record.get("title") or "") + "\n" + comments
            ticket = {
                "title": record.get("title") or "",
                "body": composite_body,
                "severity": record.get("severity") or severity,
            }
        plan = router.plan_mode(ticket)
        query_text = ticket.get("title") or ticket.get("body") or ""
        snippets = vector_search(self._bq, query_text=query_text, k=k)
        plan_header = cast(Dict[str, Any], plan["plan_header"])  # type: ignore
        sev = ticket.get("severity") or severity
        if sev:
            plan_header.setdefault("assumptions", []).append(
                f"Severity: {sev}"
            )
        md = kb_writer.render_agent_playbook(plan_header, snippets)
        ok, msg = kb_verifier.verify_agent_playbook(md)
        stats = {
            "k": len(snippets),
            "min_distance": min(
                (s.get("distance", 1.0) for s in snippets), default=1.0
            ),
            "ok": ok,
        }
        links_written = 0
        if write and ticket_id and snippets:
            for sn in snippets:
                cid = sn.get("id")
                if not cid:
                    continue
                dist = sn.get("distance") or 1.0
                score = 1.0 - float(dist)
                repo.upsert_link(ticket_id, str(cid), "evidence", score)
                links_written += 1
            summary_line = md.splitlines()[3] if md.splitlines() else ""
            repo.upsert_resolution(
                ticket_id,
                playbook_md=md,
                resolution_text=summary_line[:200],
            )
        print(
            f"[triage_ticket_stats] id={ticket_id} k={len(snippets)} ok={ok} "
            f"links={links_written} write={write}"
        )
        return {
            "ticket_id": ticket_id,
            "record": record,
            "plan": plan,
            "snippets": snippets,
            "draft_md": md,
            "draft_ok": ok,
            "verify_msg": msg,
            "stats": stats,
            "links_written": links_written,
        }

# Reflection:
# Straight mapping from spec.
# Next improvement: feed clarifier answers into retrieval.
