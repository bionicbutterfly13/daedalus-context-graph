"""Thin integration helpers for future Hermes adapters.

The core package deliberately does not import Hermes. Hermes-specific provider
code should live in an adapter package or plugin and call these stable models.
"""

from __future__ import annotations

from daedalus_context_graph.model import DecisionTrace, EntityRef


def provider_id() -> str:
    """Return the current Hermes provider id used by the local adapter."""

    return "neo4j_context_memory"


def trace_from_memory_write(
    *,
    decision_id: str,
    content: str,
    actor: str,
    scope: str,
    policy_version: str = "unversioned",
) -> DecisionTrace:
    """Create a low-resolution decision trace from a Hermes memory write.

    This is a bridge helper for early adapter work. Full MVDT capture should
    use explicit decision-trace fields instead of deriving from free text.
    """

    return DecisionTrace(
        decision_id=decision_id,
        decision_type="memory-write",
        entity_refs=(EntityRef(kind="scope", id=scope),),
        requested_by=actor,
        decided_by=actor,
        policy_version=policy_version,
        outcome="recorded",
        explanation=content,
        confidence=0.5,
        provenance={"source": "hermes-memory-write", "provider_id": provider_id()},
    )
