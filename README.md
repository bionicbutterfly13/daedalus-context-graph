# Daedalus Context Graph

Pre-alpha skeleton for **Daedalus Context Graph**, a reusable context graph kernel
for AI agents and context engineering.

Daedalus Context Graph is a small, reusable kernel for building context graphs:
scoped context cores, typed nodes and edges, provenance, decision traces,
retrieval policies, and adapter boundaries. It is designed to stay useful outside
Hermes while providing a clean path for a Hermes Agent memory-provider adapter.

Maintained by **Dr. Mani Saint-Victor / BionicButterfly13**:
[BionicButterfly.me](https://BionicButterfly.me).

## Status

This package is pre-alpha. The code is MIT licensed, but the repository remains
publicly visible once the initial skeleton is pushed.

This initial alpha exists to reserve the public package name and make the kernel installable while the API remains explicitly pre-alpha.

## Install

Install the current skeleton from PyPI after the first alpha upload:

```bash
python -m pip install daedalus-context-graph
```

For GitHub-based development:

```bash
git clone https://github.com/bionicbutterfly13/daedalus-context-graph.git
cd daedalus-context-graph
python -m pip install -e ".[dev]"
pytest -q
```

## Context Engineering Focus

The package is aimed at the current context-engineering wave: portable context
cores, provenance-aware graph memory, decision traces, retrieval policies, and
adapter surfaces for agent runtimes.

## Package Strategy

The public package is the kernel. Hermes integration stays thin and optional:

- General Python users install `daedalus-context-graph` for the context graph kernel.
- Hermes users install a Hermes plugin/provider that depends on the kernel.

## Current Skeleton

Implemented now:

- `DecisionTrace`
- `ContextGraphStore` protocol
- `EntityRef`
- `ArtifactRef`
- `EvidenceStandard`
- `WorkflowVersion`
- `InMemoryDaedalusGraph`
- Basic precedent search filters
- JSON export surface

Planned:

- Context core schema and namespace model.
- Neo4j-backed store.
- Ontology and active metadata layer.
- Governed retrieval and access policy.
- MCP server.
- Hermes adapter/provider.
- PyPI release workflow.

API reference:
[docs/API.md](docs/API.md).

Contribution guide:
[CONTRIBUTING.md](CONTRIBUTING.md).

## Local Checks

```bash
cd daedalus-context-graph
PYTHONPATH=src pytest -q
python -m compileall src
python -m build --sdist --wheel
python -m twine check dist/*
```
