from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class BudgetPolicy:
    max_input_tokens: int = 120_000
    max_output_tokens: int = 12_000
    max_cost_usd: float = 5.0
    max_retries: int = 2

    def validate(self) -> None:
        if min(self.max_input_tokens, self.max_output_tokens, self.max_retries) < 0 or self.max_cost_usd < 0:
            raise ValueError("Budget values must be non-negative")
