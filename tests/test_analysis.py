import pandas as pd
import pytest

from spendseer_analyser.analysis import (
    calculate_summary,
    get_spending_by_category,
    get_monthly_summary,
    get_available_months,
    get_transactions_for_month,
    get_expense_categories,
    create_default_budgets,
    calculate_budget_status,
    find_recurring_payments,
    detect_anomalies,
)


@pytest.fixture
def sample_transactions():
    transactions = pd.DataFrame({
        "Date": [
            "2026-04-01",
            "2026-04-05",
            "2026-04-20",
            "2026-05-01",
            "2026-05-03",
            "2026-05-10",
            "2026-05-15",
            "2026-06-01",
            "2026-06-05",
            "2026-06-15",
        ],
        "Description": [
            "Salary Payment",
            "Netflix Subscription",
            "Amazon Purchase",
            "Salary Payment",
            "Netflix Subscription",
            "Tesco Superstore",
            "Amazon Large Purchase",
            "Salary Payment",
            "Netflix Subscription",
            "Amazon Purchase",
        ],
        "Category": [
            "Income",
            "Subscriptions",
            "Shopping",
            "Income",
            "Subscriptions",
            "Groceries",
            "Shopping",
            "Income",
            "Subscriptions",
            "Shopping",
        ],
        "Type": [
            "Income",
            "Expense",
            "Expense",
            "Income",
            "Expense",
            "Expense",
            "Expense",
            "Income",
            "Expense",
            "Expense",
        ],
        "Amount": [
            950.00,
            -10.99,
            -50.00,
            950.00,
            -10.99,
            -42.35,
            -300.00,
            950.00,
            -10.99,
            -55.00,
        ],
    })

    transactions["Date"] = pd.to_datetime(transactions["Date"])

    return transactions


def test_calculate_summary(sample_transactions):
    summary = calculate_summary(sample_transactions)

    assert summary["total_income"] == pytest.approx(2850.00)
    assert summary["total_spending"] == pytest.approx(480.32)
    assert summary["net_savings"] == pytest.approx(2369.68)
    assert summary["largest_expense"] == pytest.approx(300.00)
    assert summary["transaction_count"] == 10


def test_get_spending_by_category(sample_transactions):
    spending = get_spending_by_category(sample_transactions)

    assert spending["Shopping"] == pytest.approx(405.00)
    assert spending["Subscriptions"] == pytest.approx(32.97)
    assert spending["Groceries"] == pytest.approx(42.35)


def test_get_monthly_summary(sample_transactions):
    monthly = get_monthly_summary(sample_transactions)

    assert list(monthly["Month"]) == ["2026-04", "2026-05", "2026-06"]

    may_row = monthly[monthly["Month"] == "2026-05"].iloc[0]

    assert may_row["Income"] == pytest.approx(950.00)
    assert may_row["Spending"] == pytest.approx(353.34)
    assert may_row["Net Savings"] == pytest.approx(596.66)


def test_get_available_months(sample_transactions):
    months = get_available_months(sample_transactions)

    assert months == ["2026-04", "2026-05", "2026-06"]


def test_get_transactions_for_month(sample_transactions):
    may_transactions = get_transactions_for_month(sample_transactions, "2026-05")

    assert len(may_transactions) == 4
    assert all(may_transactions["Date"].dt.to_period("M").astype(str) == "2026-05")


def test_get_expense_categories(sample_transactions):
    categories = get_expense_categories(sample_transactions)

    assert "Groceries" in categories
    assert "Shopping" in categories
    assert "Subscriptions" in categories
    assert "Income" not in categories


def test_create_default_budgets():
    categories = ["Groceries", "Shopping", "Subscriptions"]

    budgets = create_default_budgets(categories)

    assert budgets["Groceries"] == 200.0
    assert budgets["Shopping"] == 100.0
    assert budgets["Subscriptions"] == 40.0


def test_calculate_budget_status(sample_transactions):
    budgets = {
        "Groceries": 100.0,
        "Shopping": 100.0,
        "Subscriptions": 40.0,
    }

    result = calculate_budget_status(sample_transactions, "2026-05", budgets)

    shopping_row = result[result["Category"] == "Shopping"].iloc[0]

    assert shopping_row["Spent"] == pytest.approx(300.00)
    assert shopping_row["Status"] == "Over Budget"


def test_find_recurring_payments(sample_transactions):
    recurring = find_recurring_payments(
        sample_transactions,
        min_months=2,
        amount_tolerance=0.20,
        recurring_categories=["Subscriptions"]
    )

    assert not recurring.empty
    assert "Netflix Subscription" in recurring["Description"].tolist()

    netflix_row = recurring[recurring["Description"] == "Netflix Subscription"].iloc[0]

    assert netflix_row["Months Seen"] == 3
    assert netflix_row["Average Amount"] == pytest.approx(10.99)


def test_detect_anomalies(sample_transactions):
    anomalies = detect_anomalies(
        sample_transactions,
        multiplier=2.0,
        minimum_difference=20.0
    )

    assert not anomalies.empty
    assert "Amazon Large Purchase" in anomalies["Description"].tolist()

    row = anomalies[anomalies["Description"] == "Amazon Large Purchase"].iloc[0]

    assert row["Amount"] == pytest.approx(300.00)
    assert row["Category"] == "Shopping"