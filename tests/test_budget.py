import pytest
from deconnected.agent.budget import BudgetPolicy


def test_budget_defaults_are_valid():
    BudgetPolicy().validate()


def test_negative_budget_is_rejected():
    with pytest.raises(ValueError):
        BudgetPolicy(max_cost_usd=-1).validate()
