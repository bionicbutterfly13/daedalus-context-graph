"""Core data models for Daedalus Context Graph."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


class ValidationError(ValueError):
    """Raised when a context graph object is missing required structure."""


def utc_now_iso() -> str:
    """Return an ISO timestamp suitable for trace creation metadata."""

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(frozen=True)
class EntityRef:
    """Stable reference to an entity involved in a decision or workflow."""

    kind: str
    id: str
    label: str = ""

    def validate(self) -> None:
        if not self.kind.strip():
            raise ValidationError("entity kind is required")
        if not self.id.strip():
            raise ValidationError("entity id is required")

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "id": self.id, "label": self.label}


@dataclass(frozen=True)
class ArtifactRef:
    """Reference to an artifact that supports a decision trace."""

    uri: str
    kind: str = "artifact"
    title: str = ""

    def validate(self) -> None:
        if not self.uri.strip():
            raise ValidationError("artifact uri is required")

    def to_dict(self) -> dict[str, Any]:
        return {"uri": self.uri, "kind": self.kind, "title": self.title}


@dataclass(frozen=True)
class EvidenceStandard:
    """Expert calibration rule for what evidence a workflow requires."""

    id: str
    description: str
    required: bool = True
    domain: str = ""
    rationale: str = ""

    def validate(self) -> None:
        if not self.id.strip():
            raise ValidationError("evidence standard id is required")
        if not self.description.strip():
            raise ValidationError("evidence standard description is required")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "required": self.required,
            "domain": self.domain,
            "rationale": self.rationale,
        }


@dataclass(frozen=True)
class WorkflowVersion:
    """Versioned workflow definition used to judge decision-ready outputs."""

    workflow_id: str
    version: str
    name: str
    evidence_standards: tuple[EvidenceStandard, ...] = ()
    valid_from: str = field(default_factory=utc_now_iso)
    valid_until: str = ""

    def validate(self) -> None:
        if not self.workflow_id.strip():
            raise ValidationError("workflow_id is required")
        if not self.version.strip():
            raise ValidationError("workflow version is required")
        if not self.name.strip():
            raise ValidationError("workflow name is required")
        for standard in self.evidence_standards:
            standard.validate()

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "version": self.version,
            "name": self.name,
            "evidence_standards": [item.to_dict() for item in self.evidence_standards],
            "valid_from": self.valid_from,
            "valid_until": self.valid_until,
        }


@dataclass(frozen=True)
class DecisionTrace:
    """Minimum viable decision trace.

    A decision trace records who decided what, why, under which policy or
    workflow standard, with which evidence, and at what time.
    """

    decision_id: str
    decision_type: str
    entity_refs: tuple[EntityRef, ...]
    requested_by: str
    decided_by: str
    policy_version: str
    outcome: str
    explanation: str
    valid_at: str = field(default_factory=utc_now_iso)
    requested_at: str = field(default_factory=utc_now_iso)
    decided_at: str = field(default_factory=utc_now_iso)
    procedure_ref: str = ""
    workflow_version: str = ""
    inputs: Mapping[str, Any] = field(default_factory=dict)
    precedent_citations: tuple[str, ...] = ()
    artifact_refs: tuple[ArtifactRef, ...] = ()
    confidence: float = 0.0
    review_status: str = "draft"
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        required = {
            "decision_id": self.decision_id,
            "decision_type": self.decision_type,
            "requested_by": self.requested_by,
            "decided_by": self.decided_by,
            "policy_version": self.policy_version,
            "outcome": self.outcome,
            "explanation": self.explanation,
            "valid_at": self.valid_at,
        }
        missing = [name for name, value in required.items() if not str(value).strip()]
        if missing:
            raise ValidationError("decision trace missing required fields: " + ", ".join(missing))
        if not self.entity_refs:
            raise ValidationError("decision trace requires at least one entity_ref")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValidationError("confidence must be between 0.0 and 1.0")
        for entity in self.entity_refs:
            entity.validate()
        for artifact in self.artifact_refs:
            artifact.validate()

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "decision_id": self.decision_id,
            "decision_type": self.decision_type,
            "entity_refs": [item.to_dict() for item in self.entity_refs],
            "requested_by": self.requested_by,
            "decided_by": self.decided_by,
            "policy_version": self.policy_version,
            "procedure_ref": self.procedure_ref,
            "workflow_version": self.workflow_version,
            "valid_at": self.valid_at,
            "requested_at": self.requested_at,
            "decided_at": self.decided_at,
            "inputs": dict(self.inputs),
            "outcome": self.outcome,
            "explanation": self.explanation,
            "precedent_citations": list(self.precedent_citations),
            "artifact_refs": [item.to_dict() for item in self.artifact_refs],
            "confidence": float(self.confidence),
            "review_status": self.review_status,
            "provenance": dict(self.provenance),
        }
