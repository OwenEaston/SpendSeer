from io import StringIO

import pandas as pd

from spendseer_analyser.cleaning import clean_column_names, load_transactions


def test_clean_column_names_standardises_common_names():
    df = pd.DataFrame({
        "transaction date": ["2026-05-01"],
        "details": ["Tesco Superstore"],
        "value": ["-42.35"],
    })

    result = clean_column_names(df)

    assert "Date" in result.columns
    assert "Description" in result.columns
    assert "Amount" in result.columns


def test_load_transactions_reads_valid_csv():
    csv_data = StringIO(
        """Date,Description,Amount
2026-05-01,Tesco Superstore,-42.35
2026-05-02,Salary Payment,950.00
"""
    )

    transactions, errors = load_transactions(csv_data)

    assert errors == []
    assert transactions is not None
    assert len(transactions) == 2
    assert "Category" in transactions.columns
    assert "Type" in transactions.columns


def test_load_transactions_detects_missing_columns():
    csv_data = StringIO(
        """Date,Description
2026-05-01,Tesco Superstore
"""
    )

    transactions, errors = load_transactions(csv_data)

    assert transactions is None
    assert errors
    assert "Missing required column" in errors[0]


def test_load_transactions_removes_invalid_rows():
    csv_data = StringIO(
        """Date,Description,Amount
not-a-date,Tesco Superstore,-42.35
2026-05-02,Salary Payment,950.00
"""
    )

    transactions, errors = load_transactions(csv_data)

    assert errors == []
    assert len(transactions) == 1
    assert transactions.iloc[0]["Description"] == "Salary Payment"