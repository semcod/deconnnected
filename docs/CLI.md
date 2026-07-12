# CLI reference

## `deconnected scan ROOT`

Builds the evidence graph.

Options:

```text
--database-url TEXT
--testql-topology PATH
--out PATH                default: .deconnected/graph.json
```

## `deconnected report GRAPH_FILE`

Prints aggregate graph information, table usage, classifications and extraction candidates as JSON.

## `deconnected table-usage GRAPH_FILE`

Displays table reachability, static references, runtime references and test-only references.

## `deconnected classify-tables GRAPH_FILE`

Classifies table usage.

```text
--json-output
```

## `deconnected seams GRAPH_FILE`

Returns graph components ranked as extraction candidates.

## `deconnected generate-frontend-tests TOPOLOGY_FILE`

Generates TestQL-compatible frontend checks.

```text
--out PATH  default: .deconnected/generated-web.testql.toon.yaml
```

## `deconnected integrations`

Shows optional tool availability.

## `deconnected ecosystem-scan ROOT`

Runs installed external analyzers and writes a combined manifest.

```text
--target TEXT
--tools TEXT
--out PATH       default: .deconnected/ecosystem
--timeout INT    default: 900
```

## `deconnected plan-refactor GRAPH_FILE OBJECTIVE`

Creates a deterministic plan and optionally refines it through an LLM provider.

```text
--out PATH
--provider [none|litellm|claude-code]
--model TEXT
```

Default model:

```text
openrouter/deepseek/deepseek-chat
```

## `deconnected simulate-refactor REPOSITORY PLAN_FILE`

Executes an approved plan inside a Git worktree with Claude Code.

```text
--provider [claude-code]
--keep-worktree
```

The provider option is currently reserved for future providers; Claude Code is the only execution provider.

## `deconnected verify-refactor REPOSITORY PLAN_FILE`

Runs only the validation matrix declared in a plan.

```text
--out PATH  default: .deconnected/verification.json
```
