# SpendSeer

SpendSeer is a personal finance tool built with Python and Streamlit to analyse transactions and spending. The app allows users to upload CSV files, view bank transaction data, automatically categorise spending, generate monthly summaries, track budgets, detect recurring payments, flag unusual transactions, and export reports.

## Features

- Upload and clean CSV transaction data
- Automatically categorise transactions using keyword-based rules
- View dashboard summaries for income, spending, savings, and largest expenses
- Filter transactions by category, type, and description
- Generate month-by-month financial summaries
- Track monthly budgets by spending category
- Detect recurring payments such as subscriptions and bills
- Flag unusual or suspicious transactions using category-based anomaly detection
- Export cleaned transactions, reports, summaries, budgets, recurring payments, and anomaly results
- Save and load data locally using SQLite
- Generate fake demo transaction data for testing
- Unit-tested analysis, cleaning, and categorisation using pytest

## Tech Stack

- Python
- Streamlit
- Pandas
- SQLite
- pytest

## How to Run

Install the required packages:
```bash
pip install -r requirements.txt
```

Run the application:
```bash
streamlit run app.py
```

## Expected CSV Format

Uploaded CSV files must contain the following column format:
```cs
Date,Description,Amount
2026-05-01,Tesco Superstore,-42.35
2026-05-02,Netflix Subscription,-10.99
2026-05-03,Salary Payment,950.00
```


## Demo Data

Generate fake transaction data for testing by running:
```bash
python generate_demo_data.py
```

## Running Tests

Run the pytest using:
```bash
python -m pytest
```

## Screenshots

### Dashboard

![SpendSeer dashboard](screenshots\SpendSeerDashboard.png)

### Budget Tracking

![SpendSeer budget tracking](screenshots\SpendSeerDashboard.png)

### Anomaly Detection

![SpendSeer anomaly detection](screenshots\SpendSeerDashboard.png)