# Deconnected


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.6.2-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$0.15-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-1.0h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $0.1500 (1 commits)
- 👤 **Human dev:** ~$100 (1.0h @ $100/h, 30min dedup)

Generated on 2026-07-12 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---



Deconnected builds one evidence graph across frontend code, API routes, backend modules, workers, Docker services, SQL/ORM references and database tables. It helps identify safe extraction seams, probable legacy elements and refactoring risks before code is moved or removed.

Deconnected is intentionally conservative. A missing reference is evidence for investigation, not automatic permission to delete a table, endpoint or module.

## Capabilities

- static scanning of Python, JavaScript, TypeScript, SQL, PHP, Go, Java and Kotlin files;
- Python route, import, table and embedded-SQL analysis with LibCST;
- SQL table extraction with sqlglot and a lower-confidence fallback parser;
- Docker Compose and Dockerfile dependency scanning;
- optional database-schema reflection through SQLAlchemy;
- import and correlation of TestQL runtime topology;
- table usage classification from static, runtime and test evidence;
- extraction-candidate discovery from graph cohesion and boundary edges;
- optional integrations with code2llm, code2logic, redup, regix, vallm and toonic;
- constrained refactoring plans, optional LiteLLM/OpenRouter refinement and isolated Claude Code execution;
- patch-scope policy, forbidden-operation checks, repository snapshots and validation reports.

## Architecture

```text
TestQL runtime topology       LibCST / sqlglot / source scan
          │                              │
          └──────────────┬───────────────┘
                         ▼
             Unified evidence graph
                         ▼
       usage classification and seam analysis
                         ▼
           constrained refactoring plan
                         ▼
  LiteLLM/OpenRouter planning or Claude Code execution
                         ▼
 worktree → patch policy → tests → acceptance or rollback
```

## Requirements

- Python 3.10 or newer;
- Git for isolated refactoring simulations;
- optional Docker/TestQL/runtime services when those integrations are used;
- optional `claude` executable for Claude Code execution.

## Installation

Core package and development tools:

```bash
python -m pip install -e ".[dev]"
```

Browser and TestQL support:

```bash
python -m pip install -e ".[dev,gui,testql]"
playwright install chromium
```

LiteLLM/OpenRouter planning:

```bash
python -m pip install -e ".[dev,llm]"
```

Full optional ecosystem:

```bash
python -m pip install -e ".[dev,gui,testql,ecosystem,llm]"
```

External ecosystem packages are optional adapters. A missing adapter does not block the core scan.

## Quick start

### 1. Build an evidence graph

```bash
deconnected scan . --out .deconnected/graph.json
```

With a TestQL topology and reflected database schema:

```bash
deconnected scan . \
  --testql-topology .testql/topology.json \
  --database-url "$DATABASE_URL" \
  --out .deconnected/graph.json
```

### 2. Inspect usage and extraction candidates

```bash
deconnected report .deconnected/graph.json
deconnected table-usage .deconnected/graph.json
deconnected classify-tables .deconnected/graph.json
deconnected seams .deconnected/graph.json
```

Machine-readable table classifications:

```bash
deconnected classify-tables .deconnected/graph.json --json-output
```

### 3. Create frontend checks from TestQL topology

```bash
deconnected generate-frontend-tests \
  .testql/topology.json \
  --out .deconnected/generated-web.testql.toon.yaml
```

### 4. Create a constrained refactoring plan

```bash
deconnected plan-refactor \
  .deconnected/graph.json \
  "extract protocol audit feature" \
  --out .deconnected/refactor-plan.json
```

### 5. Verify or simulate the plan

```bash
deconnected verify-refactor . .deconnected/refactor-plan.json
```

Claude Code simulation inside an isolated worktree:

```bash
deconnected simulate-refactor \
  . \
  .deconnected/refactor-plan.json \
  --keep-worktree
```

## Table classifications

- `actively_used` — runtime SQL evidence exists;
- `statically_reachable` — reachable from a GUI/API/job/service entrypoint and referenced outside tests;
- `statically_referenced` — referenced, but no complete entrypoint path was proven;
- `test_only` — discovered references are limited to tests;
- `probable_legacy` — no static, runtime or test evidence was found.

`probable_legacy` is a review candidate. Before deletion, verify migrations, production traffic, external consumers, scheduled jobs, manual scripts, backups and rollback procedures.

## LLM-assisted planning with LiteLLM/OpenRouter

Set the provider key supported by the selected LiteLLM model. For OpenRouter:

```bash
export OPENROUTER_API_KEY="..."
```

Generate and refine a plan:

```bash
deconnected plan-refactor \
  .deconnected/graph.json \
  "split protocol audit into a bounded package" \
  --provider litellm \
  --model openrouter/deepseek/deepseek-chat \
  --out .deconnected/refactor-plan.json
```

The deterministic plan is created first. The model may refine it, but the returned object must validate against the `RefactorPlan` Pydantic schema.

Current limitation: CLI budget parameters are not exposed yet. `BudgetPolicy` exists in the Python API and uses conservative defaults.

## Claude Code execution

The Claude Code adapter runs `claude -p` with a restricted tool list:

```text
Read, Glob, Grep, Edit,
Bash(pytest:*), Bash(npm test:*), Bash(git diff:*), Bash(ruff:*)
```

The simulation:

1. refuses plans with blockers;
2. creates an isolated Git worktree and branch;
3. asks Claude Code to apply only the approved plan;
4. records snapshots before and after;
5. evaluates changed paths and forbidden operations;
6. runs the validation matrix only when policy passes;
7. saves the binary Git patch and reports.

The current branch is not edited directly.

## Refactoring artifacts

Each simulation writes to:

```text
.deconnected/runs/<plan-id>/
```

Artifacts:

```text
agent-result.json
policy.json
snapshot-before.json
snapshot-after.json
snapshot-diff.json
verification.json
patch.diff
```

See [docs/ARTIFACTS.md](docs/ARTIFACTS.md) for field-level interpretation.

## Optional ecosystem integrations

Check availability:

```bash
deconnected integrations
```

Run installed analyzers:

```bash
deconnected ecosystem-scan . \
  --target http://localhost:8100 \
  --tools testql,code2llm,redup,regix,vallm,toonic \
  --out .deconnected/ecosystem
```

The command writes `.deconnected/ecosystem/manifest.json` with availability, status and produced artifacts.

## Safety model

Default assumptions:

- no automatic database table drops;
- no remote pushes;
- no Git history rewriting;
- no direct work on the current branch;
- every plan contains `allowed_paths` and `forbidden_operations`;
- a scope or policy violation blocks acceptance;
- tests passing cannot override a blocked patch policy;
- a patch is retained for review even when blocked.

## Development

Run the complete test suite:

```bash
PYTHONPATH=src pytest -q
```

Compile Python sources:

```bash
python -m compileall src
```

Lint:

```bash
ruff check src tests
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [CLI reference](docs/CLI.md)
- [LLM and Claude Code setup](docs/LLM_PROVIDERS.md)
- [Refactoring workflow](docs/REFACTORING_WORKFLOW.md)
- [Artifacts](docs/ARTIFACTS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Changelog](CHANGELOG.md)

## Status

Version 0.6.1 is an experimental refactoring-analysis tool. Review generated plans and patches before merging. Database-destructive changes and public API changes require explicit human approval outside the current automated flow.


## License

Licensed under Apache-2.0.
