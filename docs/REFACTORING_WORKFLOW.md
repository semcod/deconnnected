# Refactoring workflow

## 1. Establish a baseline

```bash
git status --short
PYTHONPATH=src pytest -q
```

Commit or intentionally document local changes before agent execution.

## 2. Collect runtime topology

Use TestQL or another runtime source to exercise meaningful GUI journeys. A topology containing only the root page and assets cannot prove API or table usage.

## 3. Build the graph

```bash
deconnected scan . \
  --testql-topology .testql/topology.json \
  --database-url "$DATABASE_URL" \
  --out .deconnected/graph.json
```

## 4. Review classifications

```bash
deconnected classify-tables .deconnected/graph.json
```

Interpretation rule:

```text
probable_legacy != safe_to_delete
```

Check external services, cron jobs, manual scripts, data migrations and production traffic.

## 5. Generate the plan

```bash
deconnected plan-refactor \
  .deconnected/graph.json \
  "extract protocol audit feature"
```

Open the JSON and review:

- `allowed_paths`;
- `affected_symbols`;
- `blockers`;
- `validations`;
- `forbidden_operations`;
- `rollback`.

A plan with blockers cannot be simulated.

## 6. Run a simulation

```bash
deconnected simulate-refactor \
  . \
  .deconnected/refactor-plan.json \
  --keep-worktree
```

Keeping the worktree is recommended until the patch has been reviewed.

## 7. Inspect artifacts

```bash
cat .deconnected/runs/<plan-id>/policy.json
cat .deconnected/runs/<plan-id>/verification.json
git apply --stat .deconnected/runs/<plan-id>/patch.diff
```

## 8. Accept manually

Apply or cherry-pick only after review. Deconnected 0.6.1 does not automatically merge or push agent changes.

## Suggested approval levels

### Low risk

- dead re-export removal;
- file split with compatibility imports;
- internal rename with full tests.

### Medium risk

- module extraction across API and service layers;
- frontend feature extraction;
- worker or Docker service separation.

### High risk

- database schema changes;
- public route changes;
- event schema changes;
- authentication/authorization changes;
- deletion of dormant feature clusters.

High-risk changes should require a separate migration plan and human approval.
