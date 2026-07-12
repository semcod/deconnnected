# Architecture

## Design goal

Deconnected correlates evidence that normally lives in separate tools. It does not try to replace browser discovery, static-flow analyzers, SQL parsers or code agents. It normalizes their output into a graph and applies refactoring-specific policy.

## Layers

### Discovery

Sources include:

- repository files and imports;
- LibCST facts for Python;
- sqlglot table references;
- Docker Compose and Dockerfiles;
- SQLAlchemy database reflection;
- TestQL runtime topology;
- optional Semcod analyzers.

### Evidence graph

Typical node kinds:

```text
file, module, route, service, config, table, page, URL, asset, test
```

Typical edge kinds:

```text
imports, calls_or_defines_api, uses_table, depends_on,
foreign_key, observes_route, loads, defines_service
```

Every edge can carry evidence, confidence, runtime and test-only flags.

### Correlation

Runtime URLs are normalized and matched to static routes. This enables paths such as:

```text
page → browser request → route → source file → table
```

A complete path increases confidence. A name match by itself does not.

### Classification

Tables are classified from:

- entrypoint reachability;
- static incoming references;
- runtime references;
- test-only references.

### Refactoring planner

The rule-based planner chooses the highest-ranked extraction candidate and emits a constrained `RefactorPlan`. The plan includes:

- affected symbols;
- allowed paths;
- ordered steps;
- validations;
- assumptions;
- blockers;
- rollback instructions.

### Agent providers

- `LiteLLMProvider` refines structured plans;
- `ClaudeCodeProvider` can plan or edit a repository through `claude -p`;
- providers return `AgentRunResult` rather than directly controlling acceptance.

### Policy and verification

After an agent run:

1. snapshots are compared;
2. changed files are checked against plan scope;
3. forbidden operations are searched in the patch;
4. validations run only if policy passes;
5. all artifacts remain auditable.

## Current limitations

- JavaScript/TypeScript analysis is primarily source-pattern based rather than TypeScript Compiler API based;
- graph diff before/after is not yet a separate acceptance gate;
- runtime SQL traces are available as a library helper but are not automatically merged from arbitrary external test runs;
- `allowed_paths` enforcement is post-execution, not a filesystem sandbox;
- model cost usage is not yet collected from provider responses;
- destructive database operations are blocked by policy but no approval workflow is implemented.
