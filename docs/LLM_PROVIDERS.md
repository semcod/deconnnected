# LLM providers

## LiteLLM

Install:

```bash
python -m pip install -e ".[llm]"
```

OpenRouter example:

```bash
export OPENROUTER_API_KEY="..."

deconnected plan-refactor \
  .deconnected/graph.json \
  "extract the protocol audit feature" \
  --provider litellm \
  --model openrouter/deepseek/deepseek-chat
```

Other LiteLLM-supported providers can be selected by changing the model and setting the provider-specific environment variables.

The provider requests structured JSON matching `RefactorPlan.model_json_schema()`. Invalid JSON or schema-incompatible output fails planning.

## Python API and budget

```python
from deconnected.agent.budget import BudgetPolicy
from deconnected.agent.providers import LiteLLMProvider

provider = LiteLLMProvider(
    model="openrouter/deepseek/deepseek-chat",
    budget=BudgetPolicy(
        max_input_tokens=120_000,
        max_output_tokens=8_000,
        max_cost_usd=3.0,
        max_retries=1,
    ),
)
```

Current behavior:

- `max_output_tokens` is passed to LiteLLM;
- the policy validates configured values;
- actual provider cost and input-token enforcement are not yet implemented.

## Claude Code

Prerequisites:

```bash
claude --version
```

The default adapter command is equivalent to:

```bash
claude -p "<prompt>" \
  --output-format json \
  --allowedTools "Read,Glob,Grep,Edit,Bash(pytest:*),Bash(npm test:*),Bash(git diff:*),Bash(ruff:*)"
```

The executable, timeout and allowed tool list can be customized through the Python API:

```python
from deconnected.agent.providers import ClaudeCodeProvider

provider = ClaudeCodeProvider(
    executable="claude",
    timeout=1800,
    allowed_tools="Read,Glob,Grep,Edit,Bash(pytest:*),Bash(git diff:*)",
)
```

## Security notes

- run agents only in repositories with committed or backed-up work;
- inspect `policy.json`, `verification.json` and `patch.diff`;
- do not broaden Bash permissions without a specific reason;
- API keys should be supplied through environment variables, not committed config files;
- agent execution is not a replacement for OS/container sandboxing.
