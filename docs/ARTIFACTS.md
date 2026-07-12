# Refactoring artifacts

## `agent-result.json`

Provider status, stdout, structured output, return code and error information.

## `policy.json`

Patch-policy decision. `passed: false` means validation results must not be treated as acceptance evidence.

Typical findings:

- `scope_violation` — a changed file is outside `allowed_paths`;
- forbidden database/public API/history operation detected.

## `snapshot-before.json` and `snapshot-after.json`

Commit, dirty-state information and SHA-256 hashes for controlled files.

## `snapshot-diff.json`

Lists added, removed and modified files and whether the commit changed.

## `verification.json`

One object per validation command, including pass/fail state, output and return code.

## `patch.diff`

Binary-capable output of `git diff --binary` from the isolated worktree.

## Acceptance rule

A simulation is successful only when:

```text
agent status == success
AND policy.passed == true
AND every required validation passed
```
