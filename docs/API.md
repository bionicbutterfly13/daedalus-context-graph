# API Reference

This is the current hand-written API reference for the pre-alpha package.
Generated API docs can be added after the public API stabilizes.

## Package

```python
import daedalus_context_graph
```

Public exports:

- `ArtifactRef`
- `ContextGraphStore`
- `DecisionTrace`
- `EntityRef`
- `EvidenceStandard`
- `InMemoryDaedalusGraph`
- `ValidationError`
- `WorkflowVersion`

## DecisionTrace

`DecisionTrace` is the minimum viable decision trace. It records who decided
what, why, under which policy or workflow standard, with which evidence, and at
what time.

Required fields:

- `decision_id`
- `decision_type`
- `entity_refs`
- `requested_by`
- `decided_by`
- `policy_version`
- `outcome`
- `explanation`
- `valid_at`

Example:

```python
from daedalus_context_graph import DecisionTrace, EntityRef

trace = DecisionTrace(
    decision_id="decision-001",
    decision_type="memory-write",
    entity_refs=(EntityRef(kind="scope", id="demo"),),
    requested_by="user",
    decided_by="agent",
    policy_version="v1",
    outcome="recorded",
    explanation="Store the decision trace.",
    confidence=0.8,
)

payload = trace.to_dict()
```

## InMemoryDaedalusGraph

`InMemoryDaedalusGraph` is a deterministic local store for tests, examples, and
early adapter development.

Example:

```python
from daedalus_context_graph import InMemoryDaedalusGraph

graph = InMemoryDaedalusGraph()
graph.add_decision_trace(trace)
matches = graph.find_precedent(decision_type="memory-write")
```

## ContextGraphStore

`ContextGraphStore` is the storage protocol that future Neo4j and other backend
implementations should satisfy.

Required methods:

- `add_decision_trace(trace)`
- `get_decision_trace(decision_id)`
- `find_precedent(...)`

## Hermes Bridge Helper

```python
from daedalus_context_graph.hermes import provider_id, trace_from_memory_write
```

`provider_id()` currently returns `neo4j_context_memory` for compatibility with
the existing Hermes adapter. A future migration can introduce `daedalus_context_graph`
as the provider id after the compatibility path is designed.

`trace_from_memory_write(...)` creates a low-resolution decision trace from a
Hermes memory write. It is a bridge helper, not the final decision-trace capture
API.
