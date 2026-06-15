# to run the application, type "streamlit run app.py" into the terminal window
import streamlit as st
import pandas as pd

from spendseer_analyser.cleaning import load_transactions
from spendseer_analyser.database import (
    save_transactions,
    load_saved_transactions,
    save_budgets,
    load_saved_budgets,
    clear_database,
)
from spendseer_analyser.analysis import (
    calculate_summary,
    get_spending_by_category,
    get_recent_transactions,
    filter_transactions,
    get_monthly_summary,
    get_available_months,
    get_transactions_for_month,
    generate_monthly_report,
    get_expense_categories,
    create_default_budgets,
    calculate_budget_status,
    find_recurring_payments,
    detect_anomalies,
)


st.set_page_config(
    page_title="SpendSeer - Personal Finance Analyser",
    page_icon=None,
    layout="wide"
)


def dataframe_to_csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8")


# DEMO DATA
sample_transactions = pd.DataFrame({
    "Date": [
        "2026-04-01", "2026-04-02", "2026-04-05", "2026-04-12",
        "2026-04-20", "2026-04-25", "2026-05-01", "2026-05-02",
        "2026-05-03", "2026-05-04", "2026-05-05", "2026-05-06",
        "2026-05-12", "2026-05-20", "2026-05-25", "2026-05-28",
        "2026-06-01", "2026-06-03", "2026-06-05", "2026-06-08",
        "2026-06-15", "2026-06-20", "2026-06-25",
    ],
    "Description": [
        "Salary Payment", "Tesco Superstore", "Netflix Subscription",
        "Trainline Ticket", "Amazon Purchase", "Vodafone Phone Bill",
        "Salary Payment", "Tesco Superstore", "Netflix Subscription",
        "Trainline Ticket", "Amazon Purchase", "Costa Coffee",
        "Steam Purchase", "Water Bill", "Vodafone Phone Bill",
        "Currys Laptop Repair", "Salary Payment", "Aldi Store",
        "Netflix Subscription", "Spotify Premium", "Amazon Large Purchase",
        "Water Bill", "Vodafone Phone Bill",
    ],
    "Category": [
        "Income", "Groceries", "Subscriptions", "Transport", "Shopping",
        "Bills", "Income", "Groceries", "Subscriptions", "Transport",
        "Shopping", "Eating Out", "Entertainment", "Bills", "Bills",
        "Shopping", "Income", "Groceries", "Subscriptions", "Subscriptions",
        "Shopping", "Bills", "Bills",
    ],
    "Type": [
        "Income", "Expense", "Expense", "Expense", "Expense", "Expense",
        "Income", "Expense", "Expense", "Expense", "Expense", "Expense",
        "Expense", "Expense", "Expense", "Expense", "Income", "Expense",
        "Expense", "Expense", "Expense", "Expense", "Expense",
    ],
    "Amount": [
        950.00, -35.40, -10.99, -24.50, -52.99, -18.00,
        950.00, -42.35, -10.99, -18.50, -64.20, -4.75,
        -24.99, -26.00, -18.00, -180.00, 950.00, -29.80,
        -10.99, -5.99, -165.00, -26.00, -18.00,
    ],
})

sample_transactions["Date"] = pd.to_datetime(sample_transactions["Date"])


# SESSION SETUP
if "transactions" not in st.session_state:
    st.session_state["transactions"] = None

if "budgets" not in st.session_state:
    st.session_state["budgets"] = {}

if "database_checked" not in st.session_state:
    saved_transactions = load_saved_transactions()
    saved_budgets = load_saved_budgets()

    if saved_transactions is not None:
        st.session_state["transactions"] = saved_transactions

    if saved_budgets:
        st.session_state["budgets"] = saved_budgets

    st.session_state["database_checked"] = True


def get_current_transactions():
    if st.session_state["transactions"] is not None:
        return st.session_state["transactions"], False

    return sample_transactions, True


# SIDEBAR
st.sidebar.title("SpendSeer")
st.sidebar.caption("Personal Finance Transaction Analyser")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Upload Transactions",
        "Transactions",
        "Monthly Summary",
        "Recurring Payments",
        "Anomaly Detection",
        "Budgets",
        "Reports",
    ]
)

st.sidebar.divider()

if st.session_state["transactions"] is None:
    st.sidebar.warning("Using demo data")
else:
    st.sidebar.success("Using uploaded/saved data")
    st.sidebar.write(str(len(st.session_state["transactions"])) + " transactions loaded")

if st.sidebar.button("Clear uploaded data"):
    st.session_state["transactions"] = None
    st.session_state["budgets"] = {}
    st.rerun()

st.sidebar.divider()

st.sidebar.subheader("Local SQLite Storage")

current_transactions, using_demo_data = get_current_transactions()

if st.sidebar.button("Save current data to SQLite"):
    save_transactions(current_transactions)
    save_budgets(st.session_state["budgets"])
    st.sidebar.success("Saved to spendseer.db")

if st.sidebar.button("Load saved SQLite data"):
    saved_transactions = load_saved_transactions()
    saved_budgets = load_saved_budgets()

    if saved_transactions is None:
        st.sidebar.warning("No saved transactions found.")
    else:
        st.session_state["transactions"] = saved_transactions
        st.session_state["budgets"] = saved_budgets
        st.rerun()

if st.sidebar.button("Clear SQLite database"):
    clear_database()
    st.session_state["transactions"] = None
    st.session_state["budgets"] = {}
    st.sidebar.success("SQLite database cleared.")

st.sidebar.divider()
st.sidebar.caption("Built with Python, Streamlit, Pandas and SQLite.")


# MAIN TITLE
st.title("SpendSeer")
st.write(
    "Upload bank transaction data, categorise spending, track budgets, "
    "detect recurring payments, flag unusual transactions, and generate monthly finance summaries."
)


if page == "Dashboard":
    transactions, using_demo_data = get_current_transactions()

    st.header("Dashboard")

    if using_demo_data:
        st.info("You are currently viewing demo data. Upload a CSV file to analyse your own transactions.")

    summary = calculate_summary(transactions)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Income", f"£{summary['total_income']:,.2f}")

    with col2:
        st.metric("Total Spending", f"£{summary['total_spending']:,.2f}")

    with col3:
        st.metric("Net Savings", f"£{summary['net_savings']:,.2f}")

    with col4:
        st.metric("Largest Expense", f"£{summary['largest_expense']:,.2f}")

    st.divider()

    st.subheader("Monthly Income, Spending and Savings")

    monthly_summary = get_monthly_summary(transactions)

    if monthly_summary.empty:
        st.warning("No monthly data available.")
    else:
        chart_data = monthly_summary.set_index("Month")[
            ["Income", "Spending", "Net Savings"]
        ]
        st.line_chart(chart_data)

    st.divider()

    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("Spending by Category")

        spending = get_spending_by_category(transactions)

        if spending.empty:
            st.warning("No expense transactions found.")
        else:
            st.bar_chart(spending)

    with right_col:
        st.subheader("Recent Transactions")

        recent = get_recent_transactions(transactions)

        st.dataframe(
            recent,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    st.subheader("Extra Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Average Expense", f"£{summary['average_expense']:,.2f}")

    with col2:
        st.metric("Transactions Analysed", summary["transaction_count"])


elif page == "Upload Transactions":
    st.header("Upload Transactions")

    st.write(
        "Upload a CSV file containing your transactions. "
        "The app expects at least **Date**, **Description**, and **Amount**."
    )

    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None:
        transactions, errors = load_transactions(uploaded_file)

        if errors:
            for error in errors:
                st.error(error)

            st.warning("Please check that the CSV has the needed columns.")
        else:
            st.session_state["transactions"] = transactions
            st.session_state["budgets"] = {}

            st.success(f"Successfully loaded {len(transactions)} transactions.")

            st.write(
                "Date range:",
                transactions["Date"].min().date(),
                "to",
                transactions["Date"].max().date()
            )

            st.subheader("Preview")

            st.dataframe(
                transactions.head(20),
                use_container_width=True,
                hide_index=True
            )

            st.download_button(
                "Download cleaned transactions as CSV",
                data=dataframe_to_csv_bytes(transactions),
                file_name="cleaned_transactions.csv",
                mime="text/csv"
            )

    st.divider()

    st.subheader("Expected CSV format")

    expected_format = pd.DataFrame({
        "Date": ["2026-05-01", "2026-05-02", "2026-05-03"],
        "Description": ["Tesco Superstore", "Netflix Subscription", "Salary Payment"],
        "Amount": [-42.35, -10.99, 950.00],
    })

    st.dataframe(
        expected_format,
        use_container_width=True,
        hide_index=True
    )


elif page == "Transactions":
    transactions, using_demo_data = get_current_transactions()

    st.header("Transactions")

    if using_demo_data:
        st.info("You are currently viewing demo data. Upload a CSV file to analyse your own transactions.")

    col1, col2, col3 = st.columns(3)

    with col1:
        selected_category = st.selectbox(
            "Category",
            ["All"] + sorted(transactions["Category"].unique().tolist())
        )

    with col2:
        selected_type = st.selectbox("Type", ["All", "Income", "Expense"])

    with col3:
        search_term = st.text_input("Search description")

    filtered = filter_transactions(
        transactions,
        selected_category,
        selected_type,
        search_term
    )

    st.write(f"Showing {len(filtered)} transactions.")

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download filtered transactions as CSV",
        data=dataframe_to_csv_bytes(filtered),
        file_name="filtered_transactions.csv",
        mime="text/csv"
    )

    st.download_button(
        "Download all cleaned transactions as CSV",
        data=dataframe_to_csv_bytes(transactions),
        file_name="all_cleaned_transactions.csv",
        mime="text/csv"
    )


elif page == "Monthly Summary":
    transactions, using_demo_data = get_current_transactions()

    st.header("Monthly Summary")

    if using_demo_data:
        st.info("You are currently viewing demo data. Upload a CSV file to analyse your own transactions.")

    monthly_summary = get_monthly_summary(transactions)

    if monthly_summary.empty:
        st.warning("No monthly summary available.")
    else:
        st.subheader("Month-by-Month Breakdown")

        st.dataframe(
            monthly_summary,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download monthly summary as CSV",
            data=dataframe_to_csv_bytes(monthly_summary),
            file_name="monthly_summary.csv",
            mime="text/csv"
        )

        st.subheader("Monthly Spending Chart")

        chart_data = monthly_summary.set_index("Month")[
            ["Income", "Spending", "Net Savings"]
        ]

        st.line_chart(chart_data)


elif page == "Recurring Payments":
    transactions, using_demo_data = get_current_transactions()

    st.header("Recurring Payments")

    if using_demo_data:
        st.info("You are currently viewing demo data. Upload a CSV file to analyse your own transactions.")

    st.write(
        "This page looks for repeated payments across different months "
        "with similar descriptions and amounts."
    )

    categories = get_expense_categories(transactions)

    default_categories = []
    for category in ["Subscriptions", "Bills"]:
        if category in categories:
            default_categories.append(category)

    selected_categories = st.multiselect(
        "Categories to check",
        categories,
        default=default_categories
    )

    col1, col2 = st.columns(2)

    with col1:
        min_months = st.slider(
            "Minimum months seen",
            min_value=2,
            max_value=6,
            value=2
        )

    with col2:
        amount_tolerance = st.slider(
            "Allowed amount variation",
            min_value=0,
            max_value=50,
            value=20,
            help="20% means the payment amount can vary a bit and still count."
        )

    recurring = find_recurring_payments(
        transactions,
        min_months,
        amount_tolerance / 100,
        selected_categories if selected_categories else None
    )

    st.divider()

    if recurring.empty:
        st.warning("No recurring payments found with the current settings.")
    else:
        monthly_cost = recurring["Average Amount"].sum()
        yearly_cost = recurring["Estimated Yearly Cost"].sum()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Possible Recurring Payments", len(recurring))

        with col2:
            st.metric("Estimated Monthly Cost", f"£{monthly_cost:,.2f}")

        with col3:
            st.metric("Estimated Yearly Cost", f"£{yearly_cost:,.2f}")

        st.subheader("Detected Recurring Payments")

        st.dataframe(
            recurring,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download recurring payments as CSV",
            data=dataframe_to_csv_bytes(recurring),
            file_name="recurring_payments.csv",
            mime="text/csv"
        )

        st.subheader("Yearly Cost by Payment")

        chart_data = recurring.set_index("Description")["Estimated Yearly Cost"]
        st.bar_chart(chart_data)

        st.info("These are possible recurring payments, so they should still be checked manually.")


elif page == "Anomaly Detection":
    transactions, using_demo_data = get_current_transactions()

    st.header("Anomaly Detection")

    if using_demo_data:
        st.info("You are currently viewing demo data. Upload a CSV file to analyse your own transactions.")

    st.write(
        "This flags unusually large expenses by comparing them with the average "
        "spending in the same category."
    )

    months = get_available_months(transactions)
    month_options = ["All Months"] + months

    selected_month_option = st.selectbox(
        "Choose a month to inspect",
        month_options,
        index=0
    )

    if selected_month_option == "All Months":
        selected_month = None
    else:
        selected_month = selected_month_option

    col1, col2 = st.columns(2)

    with col1:
        multiplier = st.slider(
            "Flag transactions this many times above category average",
            min_value=1.2,
            max_value=5.0,
            value=2.0,
            step=0.1
        )

    with col2:
        minimum_difference = st.number_input(
            "Minimum difference above category average (£)",
            min_value=0.0,
            value=20.0,
            step=5.0
        )

    anomalies = detect_anomalies(
        transactions,
        selected_month,
        multiplier,
        minimum_difference
    )

    st.divider()

    if anomalies.empty:
        st.success("No unusual transactions were found with the current settings.")
    else:
        total_unusual = anomalies["Amount"].sum()
        largest_unusual = anomalies["Amount"].max()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Anomalies Found", len(anomalies))

        with col2:
            st.metric("Total Unusual Spend", f"£{total_unusual:,.2f}")

        with col3:
            st.metric("Largest Unusual Transaction", f"£{largest_unusual:,.2f}")

        st.subheader("Flagged Transactions")

        st.dataframe(
            anomalies,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download anomaly report as CSV",
            data=dataframe_to_csv_bytes(anomalies),
            file_name="anomaly_report.csv",
            mime="text/csv"
        )

        st.subheader("Anomaly Amounts")

        chart_data = anomalies.set_index("Description")["Amount"]
        st.bar_chart(chart_data)

        st.info("These are possible anomalies, not definite mistakes.")


elif page == "Budgets":
    transactions, using_demo_data = get_current_transactions()

    st.header("Budgets")

    if using_demo_data:
        st.info("You are currently viewing demo data. Upload a CSV file to analyse your own transactions.")

    months = get_available_months(transactions)

    if not months:
        st.warning("No transaction months available.")
    else:
        selected_month = st.selectbox(
            "Choose a month",
            months,
            index=len(months) - 1
        )

        categories = get_expense_categories(transactions)

        if not st.session_state["budgets"]:
            st.session_state["budgets"] = create_default_budgets(categories)

        st.subheader("Set Monthly Budgets")

        st.write("Adjust the budget for each spending category.")

        budget_cols = st.columns(2)
        updated_budgets = {}

        for index, category in enumerate(categories):
            with budget_cols[index % 2]:
                updated_budgets[category] = st.number_input(
                    label=f"{category} budget (£)",
                    min_value=0.0,
                    value=float(st.session_state["budgets"].get(category, 100.0)),
                    step=5.0,
                    key=f"budget_{category}"
                )

        st.session_state["budgets"] = updated_budgets

        st.divider()

        st.subheader(f"Budget Status for {selected_month}")

        budget_status = calculate_budget_status(
            transactions,
            selected_month,
            st.session_state["budgets"]
        )

        if budget_status.empty:
            st.warning("No budget data available.")
        else:
            total_budget = budget_status["Budget"].sum()
            total_spent = budget_status["Spent"].sum()
            total_remaining = total_budget - total_spent

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Budget", f"£{total_budget:,.2f}")

            with col2:
                st.metric("Total Spent", f"£{total_spent:,.2f}")

            with col3:
                st.metric("Remaining", f"£{total_remaining:,.2f}")

            st.dataframe(
                budget_status,
                use_container_width=True,
                hide_index=True
            )

            st.download_button(
                "Download budget status as CSV",
                data=dataframe_to_csv_bytes(budget_status),
                file_name=f"budget_status_{selected_month}.csv",
                mime="text/csv"
            )

            over_budget = budget_status[budget_status["Status"] == "Over Budget"]
            near_limit = budget_status[budget_status["Status"] == "Near Limit"]

            if not over_budget.empty:
                st.error("You are over budget in: " + ", ".join(over_budget["Category"].tolist()))
            elif not near_limit.empty:
                st.warning("You are close to your budget limit in: " + ", ".join(near_limit["Category"].tolist()))
            else:
                st.success("All categories are currently within budget.")

            st.subheader("Budget Usage Chart")

            chart_data = budget_status.set_index("Category")[["Budget", "Spent"]]
            st.bar_chart(chart_data)


elif page == "Reports":
    transactions, using_demo_data = get_current_transactions()

    st.header("Reports")

    months = get_available_months(transactions)

    if not months:
        st.warning("No report data available.")
    else:
        selected_month = st.selectbox(
            "Choose a month",
            months,
            index=len(months) - 1
        )

        st.subheader(f"Finance Report - {selected_month}")

        report = generate_monthly_report(transactions, selected_month)

        st.markdown(report)

        st.download_button(
            "Download monthly report as TXT",
            data=report,
            file_name=f"monthly_report_{selected_month}.txt",
            mime="text/plain"
        )

        st.subheader("Transactions for Selected Month")

        month_transactions = get_transactions_for_month(transactions, selected_month)

        st.dataframe(
            month_transactions,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download selected month transactions as CSV",
            data=dataframe_to_csv_bytes(month_transactions),
            file_name=f"transactions_{selected_month}.csv",
            mime="text/csv"
        )