# Troubleshooting

## `Plan has blockers`

The graph did not provide a cohesive extraction candidate or the plan contains unresolved blockers. Improve source/runtime evidence or edit the plan only after manual review.

## Claude executable not found

```bash
claude --version
```

Install/configure Claude Code and ensure it is on `PATH`.

## LiteLLM import error

```bash
python -m pip install -e ".[llm]"
```

## OpenRouter authentication failure

Verify:

```bash
test -n "$OPENROUTER_API_KEY" && echo configured
```

Do not print the key itself.

## Policy blocked a patch

Inspect:

```bash
cat .deconnected/runs/<plan-id>/policy.json
```

Do not simply widen `allowed_paths`. First decide whether the plan omitted a legitimate dependency or the agent expanded scope incorrectly.

## Empty or shallow TestQL topology

If `network_calls`, forms and links are empty, the crawl probably did not exercise the application. Add browser journeys and authenticated setup before drawing conclusions about unused API or tables.

## Database driver missing

SQLAlchemy reflection requires the driver matching the database URL, for example a PostgreSQL or MySQL driver. Install it separately.

## Tests pass but verification is reported as failed

Patch policy may have blocked the change. Policy has precedence over test success.

## Worktree remains after a failed run

This is intentional for diagnosis. Remove it manually only after inspecting artifacts, or use Git worktree commands.
