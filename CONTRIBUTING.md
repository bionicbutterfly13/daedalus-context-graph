# Contributing

Daedalus Context Graph is in pre-alpha. Contributions should keep the core library
small, typed, tested, and portable across agent platforms.

## Development Setup

```bash
git clone https://github.com/bionicbutterfly13/daedalus-context-graph.git
cd daedalus-context-graph
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest -q
```

## Quality Bar

- Add or update tests before changing behavior.
- Keep Hermes-specific runtime code out of the core package unless it is a thin
  adapter helper with no Hermes import dependency.
- Keep the public API explicit and documented.
- Preserve provenance, policy version, and timestamp fields when changing graph
  models.
- Do not add arbitrary Cypher execution or broad data export paths without an
  access-policy design.

## Pull Requests

Before opening a pull request:

```bash
python -m compileall -q src
pytest -q
python -m build --sdist --wheel
python -m twine check dist/*
```

PRs should include:

- The issue number or motivation.
- A short summary of changed behavior.
- Test evidence.
- Any migration notes for existing data or APIs.

## Spec And TDD Practice

For nontrivial features, create or update a spec before implementation. The
spec should state the user-facing behavior, acceptance criteria, tests, and
rollback/migration implications.

Use test-driven development where practical:

1. Write the failing behavior test.
2. Implement the smallest change that passes.
3. Refactor after the behavior is covered.
