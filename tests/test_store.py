from daedalus_context_graph import DecisionTrace, EntityRef, EvidenceStandard, InMemoryDaedalusGraph, WorkflowVersion
from daedalus_context_graph.hermes import provider_id, trace_from_memory_write


def make_trace(decision_id: str, entity_id: str, policy_version: str) -> DecisionTrace:
    return DecisionTrace(
        decision_id=decision_id,
        decision_type="pricing-exception",
        entity_refs=(EntityRef(kind="account", id=entity_id),),
        requested_by="user:requester",
        decided_by="user:approver",
        policy_version=policy_version,
        outcome="approved",
        explanation="Approved based on matching precedent.",
        confidence=0.8,
    )


def test_store_finds_precedent_by_entity_and_policy():
    store = InMemoryDaedalusGraph()
    store.add_decision_trace(make_trace("dec-1", "account:acme", "policy-v1"))
    store.add_decision_trace(make_trace("dec-2", "account:beta", "policy-v1"))
    store.add_decision_trace(make_trace("dec-3", "account:acme", "policy-v2"))

    rows = store.find_precedent(entity_id="account:acme", policy_version="policy-v1")

    assert [row.decision_id for row in rows] == ["dec-1"]


def test_store_exports_workflow_calibration_context():
    store = InMemoryDaedalusGraph()
    workflow = WorkflowVersion(
        workflow_id="target-biology-assessment",
        version="1.0",
        name="Target Biology Assessment",
        evidence_standards=(
            EvidenceStandard(
                id="human-genetics-required",
                description="Human genetic evidence must be addressed before recommendation.",
                domain="biopharma",
            ),
        ),
    )

    key = store.add_workflow_version(workflow)
    exported = store.export_json()

    assert key == "target-biology-assessment:1.0"
    assert "human-genetics-required" in exported
    assert "Target Biology Assessment" in exported


def test_hermes_bridge_uses_internal_provider_id():
    trace = trace_from_memory_write(
        decision_id="dec-memory-1",
        content="Remember that Daedalus Context Graph is private-first.",
        actor="user:dr-mani",
        scope="project:daedalus",
    )

    assert provider_id() == "neo4j_context_memory"
    assert trace.decision_type == "memory-write"
    assert trace.provenance["provider_id"] == "neo4j_context_memory"
