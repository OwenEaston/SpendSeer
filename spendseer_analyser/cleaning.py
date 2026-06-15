import pandas as pd

from spendseer_analyser.categorisation import categorise_transactions


REQUIRED_COLUMNS = ["Date", "Description", "Amount"]


def clean_column_names(df):
    new_names = {}

    for column in df.columns:
        clean_name = column.strip().lower()

        if clean_name in ["date", "transaction date", "posted date"]:
            new_names[column] = "Date"
        elif clean_name in ["description", "transaction description", "merchant", "details"]:
            new_names[column] = "Description"
        elif clean_name in ["amount", "transaction amount", "value"]:
            new_names[column] = "Amount"
        elif clean_name in ["type", "transaction type"]:
            new_names[column] = "Type"
        elif clean_name == "category":
            new_names[column] = "Category"

    return df.rename(columns=new_names)


def load_transactions(uploaded_file):
    errors = []

    try:
        df = pd.read_csv(uploaded_file)
    except Exception:
        return None, ["The file could not be read. Please upload a valid CSV file."]

    df = clean_column_names(df)

    missing = []
    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            missing.append(column)

    if missing:
        return None, ["Missing required column(s): " + ", ".join(missing)]

    keep_columns = ["Date", "Description", "Amount"]

    if "Type" in df.columns:
        keep_columns.append("Type")

    if "Category" in df.columns:
        keep_columns.append("Category")

    df = df[keep_columns].copy()

    # CLEAN DATA
    df["Date"] = pd.to_datetime(
        df["Date"],
        format="%Y-%m-%d",
        errors="coerce"
    )

    df["Description"] = df["Description"].astype(str).str.strip()

    df["Amount"] = (
        df["Amount"]
        .astype(str)
        .str.replace("£", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

    df = df.dropna(subset=["Date", "Description", "Amount"])

    if df.empty:
        errors.append("No valid transactions were found in the file.")
        return None, errors

    if "Type" not in df.columns:
        df["Type"] = df["Amount"].apply(
            lambda amount: "Income" if amount > 0 else "Expense"
        )

    df = categorise_transactions(df)

    return df.sort_values("Date", ascending=False), errors