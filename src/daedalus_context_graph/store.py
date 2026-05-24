"""Store protocols and in-memory implementation for Daedalus Context Graph."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Protocol

from daedalus_context_graph.model import DecisionTrace, WorkflowVersion


class ContextGraphStore(Protocol):
    """Storage boundary for decision traces and workflow context."""

    def add_decision_trace(self, trace: DecisionTrace) -> str:
        """Persist a decision trace and return its id."""

    def get_decision_trace(self, decision_id: str) -> DecisionTrace | None:
        """Return a decision trace by id."""

    def find_precedent(
        self,
        *,
        decision_type: str = "",
        entity_id: str = "",
        policy_version: str = "",
        outcome: str = "",
        limit: int = 10,
    ) -> list[DecisionTrace]:
        """Find similar or filtered decision traces."""


@dataclass
class InMemoryDaedalusGraph:
    """Deterministic in-memory store for tests and local development."""

    decisions: dict[str, DecisionTrace] = field(default_factory=dict)
    workflows: dict[str, WorkflowVersion] = field(default_factory=dict)

    def add_decision_trace(self, trace: DecisionTrace) -> str:
        trace.validate()
        self.decisions[trace.decision_id] = trace
        return trace.decision_id

    def get_decision_trace(self, decision_id: str) -> DecisionTrace | None:
        return self.decisions.get(decision_id)

    def add_workflow_version(self, workflow: WorkflowVersion) -> str:
        workflow.validate()
        key = f"{workflow.workflow_id}:{workflow.version}"
        self.workflows[key] = workflow
        return key

    def find_precedent(
        self,
        *,
        decision_type: str = "",
        entity_id: str = "",
        policy_version: str = "",
        outcome: str = "",
        limit: int = 10,
    ) -> list[DecisionTrace]:
        rows = list(self.decisions.values())
        if decision_type:
            rows = [row for row in rows if row.decision_type == decision_type]
        if entity_id:
            rows = [
                row
                for row in rows
                if any(entity.id == entity_id for entity in row.entity_refs)
            ]
        if policy_version:
            rows = [row for row in rows if row.policy_version == policy_version]
        if outcome:
            rows = [row for row in rows if row.outcome == outcome]
        rows.sort(key=lambda row: (row.valid_at, row.decision_id), reverse=True)
        return rows[: max(0, int(limit))]

    def export_json(self) -> str:
        payload: dict[str, Any] = {
            "decisions": [trace.to_dict() for trace in self.decisions.values()],
            "workflows": [workflow.to_dict() for workflow in self.workflows.values()],
        }
        return json.dumps(payload, indent=2, sort_keys=True)
