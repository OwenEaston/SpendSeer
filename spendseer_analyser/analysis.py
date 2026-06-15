import pandas as pd


def calculate_summary(transactions):
    income = transactions.loc[transactions["Amount"] > 0, "Amount"].sum()
    spending = transactions.loc[transactions["Amount"] < 0, "Amount"].sum()

    expenses = transactions[transactions["Amount"] < 0]

    if expenses.empty:
        largest_expense = 0
        average_expense = 0
    else:
        largest_expense = abs(expenses["Amount"].min())
        average_expense = abs(expenses["Amount"].mean())

    return {
        "total_income": income,
        "total_spending": abs(spending),
        "net_savings": income + spending,
        "largest_expense": largest_expense,
        "average_expense": average_expense,
        "transaction_count": len(transactions),
    }


def get_spending_by_category(transactions):
    spending = (
        transactions[transactions["Amount"] < 0]
        .groupby("Category")["Amount"]
        .sum()
        .abs()
        .sort_values(ascending=False)
    )

    return spending


def get_recent_transactions(transactions, limit=10):
    return transactions.sort_values("Date", ascending=False).head(limit)


def filter_transactions(transactions, selected_category="All", selected_type="All", search_term=""):
    filtered = transactions.copy()

    if selected_category != "All":
        filtered = filtered[filtered["Category"] == selected_category]

    if selected_type != "All":
        filtered = filtered[filtered["Type"] == selected_type]

    if search_term:
        filtered = filtered[
            filtered["Description"].str.contains(search_term, case=False, na=False)
        ]

    return filtered


def get_monthly_summary(transactions):
    if transactions.empty:
        return pd.DataFrame(
            columns=["Month", "Income", "Spending", "Net Savings", "Transaction Count"]
        )

    df = transactions.copy()
    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    income = df[df["Amount"] > 0].groupby("Month")["Amount"].sum()
    spending = df[df["Amount"] < 0].groupby("Month")["Amount"].sum().abs()
    count = df.groupby("Month")["Amount"].count()

    monthly = pd.DataFrame({
        "Income": income,
        "Spending": spending,
        "Transaction Count": count
    }).fillna(0)

    monthly["Net Savings"] = monthly["Income"] - monthly["Spending"]
    monthly = monthly.reset_index().sort_values("Month")

    return monthly


def get_available_months(transactions):
    if transactions.empty:
        return []

    months = (
        transactions["Date"]
        .dt.to_period("M")
        .astype(str)
        .sort_values()
        .unique()
        .tolist()
    )

    return months


def get_transactions_for_month(transactions, selected_month):
    df = transactions.copy()
    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    month_data = df[df["Month"] == selected_month].copy()
    return month_data.drop(columns=["Month"])


def get_top_category_for_month(transactions, selected_month):
    month_data = get_transactions_for_month(transactions, selected_month)
    spending = get_spending_by_category(month_data)

    if spending.empty:
        return "None", 0

    return spending.index[0], spending.iloc[0]


def generate_monthly_report(transactions, selected_month):
    month_data = get_transactions_for_month(transactions, selected_month)
    summary = calculate_summary(month_data)

    top_category, top_amount = get_top_category_for_month(transactions, selected_month)

    report = f"""
In **{selected_month}**, you had **{summary["transaction_count"]}** transactions.

Total income: **£{summary["total_income"]:,.2f}**

Total spending: **£{summary["total_spending"]:,.2f}**

Net savings: **£{summary["net_savings"]:,.2f}**

Largest single expense: **£{summary["largest_expense"]:,.2f}**

Average expense: **£{summary["average_expense"]:,.2f}**

Your highest spending category was **{top_category}**, with **£{top_amount:,.2f}** spent.
"""

    return report


def get_expense_categories(transactions):
    categories = (
        transactions[transactions["Amount"] < 0]["Category"]
        .dropna()
        .sort_values()
        .unique()
        .tolist()
    )

    return categories


def create_default_budgets(categories):
    defaults = {
        "Groceries": 200.0,
        "Transport": 100.0,
        "Eating Out": 80.0,
        "Shopping": 100.0,
        "Subscriptions": 40.0,
        "Entertainment": 50.0,
        "Bills": 150.0,
        "Uncategorised": 50.0,
    }

    budgets = {}

    for category in categories:
        budgets[category] = defaults.get(category, 100.0)

    return budgets


def calculate_budget_status(transactions, selected_month, budgets):
    month_data = get_transactions_for_month(transactions, selected_month)
    spending = get_spending_by_category(month_data)

    rows = []

    for category, budget in budgets.items():
        spent = spending.get(category, 0)
        remaining = budget - spent

        if budget > 0:
            used_percent = (spent / budget) * 100
        else:
            used_percent = 0

        if spent > budget:
            status = "Over Budget"
        elif used_percent >= 80:
            status = "Near Limit"
        else:
            status = "On Track"

        rows.append({
            "Category": category,
            "Budget": round(budget, 2),
            "Spent": round(spent, 2),
            "Remaining": round(remaining, 2),
            "Used %": round(used_percent, 1),
            "Status": status,
        })

    budget_status = pd.DataFrame(rows)

    if budget_status.empty:
        return budget_status

    return budget_status.sort_values("Used %", ascending=False)


def normalise_description(description):
    return (
        str(description)
        .lower()
        .replace(".", "")
        .replace(",", "")
        .replace("-", " ")
        .strip()
    )

# group similar payments by description and category
def find_recurring_payments(transactions, min_months=2, amount_tolerance=0.20, recurring_categories=None):
    if transactions.empty:
        return pd.DataFrame()

    df = transactions.copy()
    df = df[df["Amount"] < 0]

    if recurring_categories is None:
        recurring_categories = ["Subscriptions", "Bills"]

    df = df[df["Category"].isin(recurring_categories)]

    if df.empty:
        return pd.DataFrame()

    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    df["Clean Description"] = df["Description"].apply(normalise_description)
    df["Absolute Amount"] = df["Amount"].abs()

    rows = []

    grouped = df.groupby(["Clean Description", "Category"])

    for (_, category), group in grouped:
        months_seen = sorted(group["Month"].unique().tolist())

        if len(months_seen) < min_months:
            continue

        avg_amount = group["Absolute Amount"].mean()
        min_amount = group["Absolute Amount"].min()
        max_amount = group["Absolute Amount"].max()

        if avg_amount == 0:
            continue

        variation = (max_amount - min_amount) / avg_amount

        if variation <= amount_tolerance:
            name = group["Description"].mode().iloc[0]

            rows.append({
                "Description": name,
                "Category": category,
                "Average Amount": round(avg_amount, 2),
                "Times Seen": len(group),
                "Months Seen": len(months_seen),
                "First Seen": group["Date"].min().date(),
                "Last Seen": group["Date"].max().date(),
                "Amount Variation %": round(variation * 100, 1),
                "Estimated Yearly Cost": round(avg_amount * 12, 2),
            })

    recurring = pd.DataFrame(rows)

    if recurring.empty:
        return recurring

    return recurring.sort_values("Estimated Yearly Cost", ascending=False)

# compare transactions against the average for their category
def detect_anomalies(transactions, selected_month=None, multiplier=2.0, minimum_difference=20.0):
    if transactions.empty:
        return pd.DataFrame()

    df = transactions.copy()
    df = df[df["Amount"] < 0]

    if df.empty:
        return pd.DataFrame()

    df["Absolute Amount"] = df["Amount"].abs()
    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    all_data = df.copy()

    if selected_month is None:
        check_data = df.copy()
    else:
        check_data = df[df["Month"] == selected_month].copy()

    if check_data.empty:
        return pd.DataFrame()

    # compare against usual category spend
    category_stats = (
        all_data
        .groupby("Category")["Absolute Amount"]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={
            "mean": "Category Average",
            "count": "Category Transaction Count"
        })
    )

    check_data = check_data.merge(category_stats, on="Category", how="left")

    rows = []

    for _, row in check_data.iterrows():
        category_average = row["Category Average"]

        if pd.isna(category_average) or category_average == 0:
            continue

        difference = row["Absolute Amount"] - category_average

        is_unusual = (
            row["Absolute Amount"] >= category_average * multiplier
            and difference >= minimum_difference
        )

        if is_unusual:
            rows.append({
                "Date": row["Date"].date(),
                "Description": row["Description"],
                "Category": row["Category"],
                "Amount": round(row["Absolute Amount"], 2),
                "Category Average": round(category_average, 2),
                "Difference": round(difference, 2),
                "Times Higher Than Average": round(row["Absolute Amount"] / category_average, 2),
                "Reason": f"Much higher than usual for {row['Category']}",
            })

    anomalies = pd.DataFrame(rows)

    if anomalies.empty:
        return anomalies

    return anomalies.sort_values("Difference", ascending=False)