import pytest

from daedalus_context_graph import DecisionTrace, EntityRef, ValidationError


def test_decision_trace_requires_entity_refs():
    trace = DecisionTrace(
        decision_id="dec-1",
        decision_type="approval",
        entity_refs=(),
        requested_by="user:requester",
        decided_by="user:approver",
        policy_version="policy-v1",
        outcome="approved",
        explanation="Approved because precedent matched.",
    )

    with pytest.raises(ValidationError, match="entity_ref"):
        trace.validate()


def test_decision_trace_serializes_minimum_viable_trace():
    trace = DecisionTrace(
        decision_id="dec-2",
        decision_type="pricing-exception",
        entity_refs=(EntityRef(kind="account", id="account:acme"),),
        requested_by="user:requester",
        decided_by="user:approver",
        policy_version="renewal-policy-v3.2",
        outcome="approved",
        explanation="Strategic account matched Q4 expansion precedent.",
        precedent_citations=("dec-1",),
        confidence=0.82,
    )

    payload = trace.to_dict()

    assert payload["decision_id"] == "dec-2"
    assert payload["entity_refs"][0]["id"] == "account:acme"
    assert payload["precedent_citations"] == ["dec-1"]
    assert payload["confidence"] == 0.82
