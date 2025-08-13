"""Agent Playbook v0 writer.
"""
from __future__ import annotations
from typing import Dict, List, Any

SECTIONS = [
    "# Agent Playbook",
    "## Summary",
    "## Diagnostics",
    "## Next Steps",
    "## References",
]


def render_agent_playbook(
    plan_header: Dict[str, Any], snippets: List[Dict[str, Any]]
) -> str:
    """Render markdown playbook.

    Parameters
    ----------
    plan_header: dict with 'summary' and optional 'assumptions'
    snippets: list of retrieval dicts
    """
    lines: List[str] = []
    lines.append(SECTIONS[0])
    lines.append("")
    lines.append(SECTIONS[1])
    lines.append(plan_header.get("summary", "(no summary)"))
    assumptions = plan_header.get("assumptions") or []
    if assumptions:
        lines.append("")
        lines.append("Assumptions:")
        for a in assumptions:
            lines.append(f"- {a}")
    lines.append("")
    lines.append(SECTIONS[2])
    lines.append(
        "(Add diagnostics steps here – logs, reproduction, scope checks.)"
    )
    lines.append("")
    lines.append(SECTIONS[3])
    lines.append("1. Investigate top suspected root cause.")
    lines.append("2. Collect additional metrics or error samples.")
    lines.append("3. Prepare mitigation or rollback plan.")
    lines.append("")
    lines.append(SECTIONS[4])
    for snip in snippets[:8]:
        lines.append(
            f"- [chunk:{snip.get('id')}] dist={snip.get('distance'):.4f}"
            if isinstance(snip.get("distance"), (int, float))
            else f"- [chunk:{snip.get('id')}]"
        )
    return "\n".join(lines) + "\n"

# Reflection:
# Minimal markdown renderer; next improvement: add citation context excerpts.
