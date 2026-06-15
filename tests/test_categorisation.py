import pandas as pd

from spendseer_analyser.categorisation import (
    categorise_description,
    categorise_transactions,
)


def test_categorise_income_positive_amount():
    result = categorise_description("Salary Payment", 950.00)

    assert result == "Income"


def test_categorise_groceries():
    result = categorise_description("Tesco Superstore", -42.35)

    assert result == "Groceries"


def test_categorise_subscriptions():
    result = categorise_description("Netflix Subscription", -10.99)

    assert result == "Subscriptions"


def test_categorise_unknown_transaction():
    result = categorise_description("Random Unknown Shop", -12.50)

    assert result == "Uncategorised"


def test_categorise_transactions_adds_category_column():
    transactions = pd.DataFrame({
        "Description": [
            "Tesco Superstore",
            "Netflix Subscription",
            "Salary Payment",
            "Unknown Shop",
        ],
        "Amount": [-42.35, -10.99, 950.00, -8.50],
    })

    result = categorise_transactions(transactions)

    assert "Category" in result.columns
    assert result.loc[0, "Category"] == "Groceries"
    assert result.loc[1, "Category"] == "Subscriptions"
    assert result.loc[2, "Category"] == "Income"
    assert result.loc[3, "Category"] == "Uncategorised"