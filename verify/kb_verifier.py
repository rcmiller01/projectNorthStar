"""Agent Playbook verifier (structure + citations).
"""
from __future__ import annotations
from typing import Tuple

REQUIRED_HEADINGS = [
    "# Agent Playbook",
    "## Summary",
    "## Diagnostics",
    "## Next Steps",
    "## References",
]


def verify_agent_playbook(md: str) -> Tuple[bool, str]:
    """Verify structural sections and presence of at least one citation.

    Returns (ok, message)
    """
    missing = [h for h in REQUIRED_HEADINGS if h not in md]
    if missing:
        return False, f"Missing sections: {', '.join(missing)}"
    if "[chunk:" not in md:
        return False, "No chunk citations found"
    return True, "ok"

# Reflection:
# Basic structural verifier; next: enforce ordering and unique chunk IDs.
