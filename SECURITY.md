# Security Policy

Daedalus Context Graph is pre-alpha. Security-sensitive behavior should be conservative
by default.

## Supported Versions

Only the latest pre-alpha release is supported.

## Reporting A Vulnerability

Report security issues privately to:

- Website: https://BionicButterfly.me
- GitHub owner: `BionicButterfly13`

Do not open a public issue for secrets, credential exposure, authorization
bypass, data leakage, or unsafe export behavior.

## Security Expectations

- No real credentials in examples, tests, logs, or issue templates.
- No raw transcript export by default.
- No arbitrary Cypher execution exposed through public APIs by default.
- Context retrieval should be scope-aware and policy-gated before it becomes a
  production feature.
- Release artifacts should be built by CI before public distribution.
