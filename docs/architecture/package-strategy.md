# Package Strategy

Status: initial architecture decision.

## Decision

Build Daedalus Context Graph as a reusable Python library first, then ship platform
adapters around it.

## Layout

Initial local staging path:

```text
daedalus-context-graph/
```

Future private GitHub repository:

```text
daedalus-context-graph/
  pyproject.toml
  src/daedalus_context_graph/
  tests/
  docs/
```

## Install Surfaces

### Core Library

For Python projects and scripts:

```bash
pip install daedalus-context-graph
```

Import surface:

```python
from daedalus_context_graph import DecisionTrace, InMemoryDaedalusGraph
```

### Hermes Adapter

For Hermes users:

```bash
pip install "daedalus-context-graph[neo4j]"
hermes memory setup daedalus-context-graph
```

The exact Hermes command is a future implementation detail. The core rule is
that Hermes should call the library through a thin adapter/provider.

### MCP Server

For non-Hermes agents:

```bash
daedalus-context-graph-mcp
```

The MCP surface should expose policy-gated context operations, not arbitrary
Cypher.

## Boundaries

Core library responsibilities:

- domain models
- validation
- store protocols
- in-memory store
- Neo4j store
- export/import
- context quality checks

Hermes adapter responsibilities:

- Hermes `MemoryProvider` lifecycle
- Hermes tool schemas
- provider setup/uninstall checks
- config/environment integration

MCP adapter responsibilities:

- local stdio server
- tool schemas for non-Hermes agents
- access-policy aware retrieval

## Private-First Release Path

1. Local skeleton.
2. Private GitHub repository.
3. Internal alpha package builds.
4. Private TestPyPI rehearsal.
5. Public PyPI only after license, docs, API, tests, and positioning are ready.
