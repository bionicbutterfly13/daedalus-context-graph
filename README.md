# Daedalus Context Graph

A small, dependency-free Python kernel for **decision traces**, **evidence
standards**, and **precedent lookup** in AI agent context layers.

Most agent memory stores what was said. Daedalus Context Graph stores what was
**decided**: who asked, who decided, under which policy or workflow version,
on what evidence, with what confidence, and when. That record is what lets an
agent (or a human reviewing it) find precedent, audit a call, and calibrate the
next one.

Maintained by **Dr. Mani Saint-Victor / BionicButterfly13**
([BionicButterfly.me](https://BionicButterfly.me)). MIT licensed. Python 3.10+.
No runtime dependencies.

> Daedalus Context Graph is a governed context graph and calibration graph
> library for AI agents, with a Hermes adapter and Neo4j backend.

## Status

**Pre-alpha, 0.1.0a0.** The kernel below is implemented, typed, tested, and on
PyPI. The Neo4j store, ontology layer, governed retrieval, and MCP server are
not in this package yet (see Roadmap). Breaking changes may happen between
`0.1.0a*` releases.

What exists today:

| Piece | State |
|---|---|
| Core models (`DecisionTrace`, `EntityRef`, `ArtifactRef`, `EvidenceStandard`, `WorkflowVersion`) | Implemented, validated, JSON-exportable |
| `ContextGraphStore` protocol | Implemented (the boundary a Neo4j or other backend must satisfy) |
| `InMemoryDaedalusGraph` | Implemented: add, get, filtered precedent search, JSON export |
| Hermes bridge helpers (`daedalus_context_graph.hermes`) | Implemented: provider id constant, memory-write to decision-trace mapping |
| Tests, CI (Python 3.10 to 3.12), PyPI trusted publishing | In place |
| Neo4j-backed store, ontology, access policy, MCP server | Planned |

## Install

```bash
python -m pip install daedalus-context-graph
```

For development:

```bash
git clone https://github.com/bionicbutterfly13/daedalus-context-graph.git
cd daedalus-context-graph
python -m pip install -e ".[dev]"
pytest -q
```

## Quick start

Record a decision, then find precedent for the next one.

```python
from daedalus_context_graph import (
    ArtifactRef,
    DecisionTrace,
    EntityRef,
    EvidenceStandard,
    InMemoryDaedalusGraph,
    WorkflowVersion,
)

graph = InMemoryDaedalusGraph()

# 1. Declare what evidence a workflow requires before an output is decision-ready.
workflow = WorkflowVersion(
    workflow_id="vendor-approval",
    version="2",
    name="Vendor approval",
    evidence_standards=(
        EvidenceStandard(
            id="two-references",
            description="Two independent references checked",
            domain="procurement",
            rationale="Single references were wrong in 3 of 10 past approvals",
        ),
    ),
)
graph.add_workflow_version(workflow)

# 2. Record the decision itself: who, what, why, under which policy, on what evidence.
trace = DecisionTrace(
    decision_id="dec-2026-0912",
    decision_type="vendor-approval",
    entity_refs=(EntityRef(kind="vendor", id="acme-labs", label="Acme Labs"),),
    requested_by="ops-agent",
    decided_by="dr-mani",
    policy_version="procurement-v2",
    workflow_version="vendor-approval:2",
    outcome="approved",
    explanation="Both references confirmed on-time delivery; pricing within band.",
    artifact_refs=(ArtifactRef(uri="s3://evidence/acme-refs.pdf", title="Reference calls"),),
    confidence=0.85,
    review_status="final",
)
graph.add_decision_trace(trace)

# 3. Next time the same vendor comes up, pull precedent instead of re-deciding blind.
for prior in graph.find_precedent(entity_id="acme-labs", outcome="approved"):
    print(prior.decision_id, prior.decided_by, prior.confidence, prior.explanation)

# 4. Export the whole graph as JSON for another store, a review, or a diff.
payload = graph.export_json()
```

Every model validates on write. A trace with no `entity_refs`, a confidence
outside `[0, 1]`, or a blank required field raises `ValidationError` rather than
landing in the store.

## Data model

```text
WorkflowVersion ──has──▶ EvidenceStandard (id, description, required, domain, rationale)
      ▲
      │ workflow_version (string ref)
DecisionTrace
  ├─ entity_refs   ──▶ EntityRef   (kind, id, label)
  ├─ artifact_refs ──▶ ArtifactRef (uri, kind, title)
  ├─ precedent_citations (decision ids)
  ├─ requested_by / decided_by / policy_version / procedure_ref
  ├─ requested_at / decided_at / valid_at   (UTC ISO-8601)
  ├─ inputs, outcome, explanation
  ├─ confidence (0.0 to 1.0), review_status
  └─ provenance (free-form mapping)
```

`DecisionTrace` is the **minimum viable decision trace (MVDT)**: the smallest
record that still answers "why did the system do that?" a year later. Fields
required at validation: `decision_id`, `decision_type`, `entity_refs`,
`requested_by`, `decided_by`, `policy_version`, `outcome`, `explanation`,
`valid_at`.

`EvidenceStandard` and `WorkflowVersion` carry **expert calibration**: the
thresholds a domain expert applies before trusting an output. They are versioned
with `valid_from` / `valid_until` so a decision can always be judged against the
standard that was in force when it was made.

## Store boundary

```python
class ContextGraphStore(Protocol):
    def add_decision_trace(self, trace: DecisionTrace) -> str: ...
    def get_decision_trace(self, decision_id: str) -> DecisionTrace | None: ...
    def find_precedent(self, *, decision_type="", entity_id="", policy_version="",
                       outcome="", limit=10) -> list[DecisionTrace]: ...
```

`InMemoryDaedalusGraph` satisfies it and is deterministic (results sort by
`valid_at` then `decision_id`, newest first), which makes it the reference for
tests and for any backend implementation. A Neo4j store is the next backend.

## How it fits with Hermes Agent and Neo4j

```text
┌──────────────────────────────┐
│  Hermes Agent (runtime)      │  memory.provider: neo4j_context_graph
└──────────────┬───────────────┘
               │ official MemoryProvider contract
┌──────────────▼───────────────┐
│  hermes-neo4j-context-graph  │  Hermes adapter (separate package)
│  provider id:                │  sync_turn → queued graph writes
│  neo4j_context_graph         │  prefetch  → bounded decision-first recall
│                              │  tools     → read-only search / read
└──────────────┬───────────────┘
               │ uses models + store protocol from
┌──────────────▼───────────────┐
│  daedalus-context-graph      │  this package: kernel, no Hermes import
└──────────────┬───────────────┘
               │ ContextGraphStore
┌──────────────▼───────────────┐
│  Neo4j                       │  Session, Turn, Decision, Concept, Entity,
│                              │  ToolCall, ProviderEvent (+ provenance edges)
└──────────────────────────────┘
```

The kernel deliberately does not import Hermes. `daedalus_context_graph.hermes`
holds two bridge helpers only:

- `provider_id()` returns `"neo4j_context_memory"`, the provider id the current
  local adapter uses, so the kernel and adapter agree on naming.
- `trace_from_memory_write(...)` turns a Hermes built-in memory write into a
  low-resolution `DecisionTrace` (type `memory-write`, confidence 0.5,
  provenance `hermes-memory-write`) so nothing an agent remembers is lost from
  the decision record even before explicit decision capture exists.

The companion adapter, `hermes-neo4j-context-graph`, has a local proof of the
full Hermes provider lifecycle against Neo4j: explicit activation through
`memory.provider`, non-blocking queued turn and decision writes, first-class
`Decision` nodes linked to their source turns and concepts, bounded recall
through `prefetch()`, two read-only provider tools (`neo4j_context_graph_search`,
`neo4j_context_graph_read`), visible degraded status when Neo4j is down, and a
STRIDE review with all eight threats closed. That adapter repository is private
for now; its PyPI name is reserved at `0.1.0a0`.

## Roadmap

1. `Neo4jContextGraphStore` implementing `ContextGraphStore` inside this
   package, with idempotent schema bootstrap.
2. Context core schema and namespace model (per-profile scoping inside one
   shared graph).
3. Ontology and active metadata layer for `Concept` and `Entity` derivation.
4. Governed retrieval and access policy (task-shaped reads, never raw
   model-callable Cypher).
5. MCP server exposing policy-gated context operations to non-Hermes agents.
6. Promote the proven Hermes adapter out of private and onto the kernel's
   `ContextGraphStore`.

## Documentation

- [docs/API.md](docs/API.md): hand-written API reference.
- [docs/architecture/package-strategy.md](docs/architecture/package-strategy.md):
  kernel-first packaging and adapter boundaries.
- [docs/product/naming.md](docs/product/naming.md): why Daedalus.
- [CHANGELOG.md](CHANGELOG.md), [CONTRIBUTING.md](CONTRIBUTING.md),
  [SECURITY.md](SECURITY.md).

## Local checks

```bash
PYTHONPATH=src pytest -q
python -m compileall src
python -m build --sdist --wheel
python -m twine check dist/*
```
