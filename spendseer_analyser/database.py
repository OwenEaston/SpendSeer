import sqlite3

import pandas as pd


DB_NAME = "spendseer.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def ensure_database_exists():
    connection = get_connection()
    cursor = connection.cursor()

    # DATABASE TABLES
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS budgets (
            category TEXT PRIMARY KEY,
            amount REAL NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()


def save_transactions(transactions):
    ensure_database_exists()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM transactions")

    for _, row in transactions.iterrows():
        date_value = row["Date"]

        if hasattr(date_value, "strftime"):
            date_value = date_value.strftime("%Y-%m-%d")
        else:
            date_value = str(date_value)[:10]

        cursor.execute(
            """
            INSERT INTO transactions (date, description, category, type, amount)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                date_value,
                str(row["Description"]),
                str(row["Category"]),
                str(row["Type"]),
                float(row["Amount"]),
            )
        )

    connection.commit()
    connection.close()


def load_saved_transactions():
    ensure_database_exists()

    connection = get_connection()

    transactions = pd.read_sql_query(
        """
        SELECT
            date AS Date,
            description AS Description,
            category AS Category,
            type AS Type,
            amount AS Amount
        FROM transactions
        ORDER BY date DESC
        """,
        connection
    )

    connection.close()

    if transactions.empty:
        return None

    transactions["Date"] = pd.to_datetime(
        transactions["Date"],
        format="%Y-%m-%d",
        errors="coerce"
    )

    return transactions


def clear_saved_transactions():
    ensure_database_exists()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM transactions")

    connection.commit()
    connection.close()


def save_budgets(budgets):
    ensure_database_exists()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM budgets")

    for category, amount in budgets.items():
        cursor.execute(
            """
            INSERT INTO budgets (category, amount)
            VALUES (?, ?)
            """,
            (str(category), float(amount))
        )

    connection.commit()
    connection.close()


def load_saved_budgets():
    ensure_database_exists()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT category, amount FROM budgets")
    rows = cursor.fetchall()

    connection.close()

    budgets = {}

    for category, amount in rows:
        budgets[category] = amount

    return budgets


def clear_saved_budgets():
    ensure_database_exists()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM budgets")

    connection.commit()
    connection.close()


def clear_database():
    clear_saved_transactions()
    clear_saved_budgets()