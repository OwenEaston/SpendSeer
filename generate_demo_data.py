from pathlib import Path
import random
from datetime import date

import pandas as pd


OUTPUT_PATH = Path("data/generated_demo_transactions.csv")


SALARY_NAMES = ["Salary Payment", "Payroll Payment"]

GROCERIES = [
    "Tesco Superstore", "Aldi Store", "Sainsburys", "Lidl", "Asda Groceries"
]

TRANSPORT = [
    "Trainline Ticket", "Uber Trip", "Bus Fare", "Shell Fuel"
]

EATING_OUT = [
    "Costa Coffee", "Greggs", "McDonalds", "Subway", "Starbucks"
]

SHOPPING = [
    "Amazon Purchase", "Primark", "Currys", "Argos", "eBay"
]

ENTERTAINMENT = [
    "Steam Purchase", "Cineworld", "Vue Cinema", "Epic Games"
]

MONTHLY_PAYMENTS = [
    ("Netflix Subscription", -10.99, 5),
    ("Spotify Premium", -5.99, 8),
    ("Vodafone Phone Bill", -18.00, 25),
    ("Water Bill", -26.00, 20),
]

BIG_PURCHASES = [
    ("Amazon Large Purchase", -165.00),
    ("Currys Laptop Repair", -180.00),
    ("Trainline Long Distance Ticket", -120.00),
]


def get_random_date(year, month):
    return date(year, month, random.randint(1, 28))


def add_row(rows, trans_date, description, amount):
    rows.append({
        "Date": trans_date.strftime("%Y-%m-%d"),
        "Description": description,
        "Amount": round(amount, 2),
    })


def generate_demo_transactions(start_year=2026, start_month=1, number_of_months=12, seed=42):
    random.seed(seed)

    rows = []
    year = start_year
    month = start_month

    for month_number in range(number_of_months):
        add_row(
            rows,
            date(year, month, 1),
            random.choice(SALARY_NAMES),
            950.00
        )

        # recurring bills/subscriptions
        for description, amount, day in MONTHLY_PAYMENTS:
            add_row(rows, date(year, month, min(day, 28)), description, amount)

        for _ in range(random.randint(4, 7)):
            add_row(rows, get_random_date(year, month), random.choice(GROCERIES), -random.uniform(15, 55))

        for _ in range(random.randint(2, 4)):
            add_row(rows, get_random_date(year, month), random.choice(TRANSPORT), -random.uniform(5, 35))

        for _ in range(random.randint(3, 6)):
            add_row(rows, get_random_date(year, month), random.choice(EATING_OUT), -random.uniform(3, 18))

        for _ in range(random.randint(2, 4)):
            add_row(rows, get_random_date(year, month), random.choice(SHOPPING), -random.uniform(10, 75))

        for _ in range(random.randint(1, 3)):
            add_row(rows, get_random_date(year, month), random.choice(ENTERTAINMENT), -random.uniform(8, 35))

        # a few larger payments for the anomaly page
        if month_number in [4, 8, 10]:
            description, amount = random.choice(BIG_PURCHASES)
            add_row(rows, get_random_date(year, month), description, amount)

        month += 1

        if month > 12:
            month = 1
            year += 1

    transactions = pd.DataFrame(rows)
    transactions["Date"] = pd.to_datetime(transactions["Date"])
    transactions = transactions.sort_values("Date")

    return transactions


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    transactions = generate_demo_transactions()
    transactions.to_csv(OUTPUT_PATH, index=False)

    print("Generated demo data:", OUTPUT_PATH)
    print("Rows created:", len(transactions))


if __name__ == "__main__":
    main()