import pandas as pd


CATEGORY_RULES = {
    "Groceries": [
        "tesco", "sainsbury", "sainsburys", "asda", "morrisons",
        "aldi", "lidl", "waitrose", "co-op", "coop", "iceland"
    ],
    "Subscriptions": [
        "netflix", "spotify", "disney", "prime video", "amazon prime",
        "youtube premium", "apple", "icloud", "microsoft", "xbox",
        "playstation"
    ],
    "Transport": [
        "trainline", "uber", "bolt", "bus", "rail", "national express",
        "first bus", "stagecoach", "shell", "bp", "esso", "parking"
    ],
    "Eating Out": [
        "mcdonald", "kfc", "burger king", "subway", "greggs", "costa",
        "starbucks", "nero", "dominos", "pizza hut", "nandos"
    ],
    "Shopping": [
        "amazon", "ebay", "argos", "currys", "game", "cex", "hmv",
        "primark", "zara", "h&m", "matalan"
    ],
    "Entertainment": [
        "cinema", "odeon", "vue", "cineworld", "steam", "riot games",
        "epic games", "twitch"
    ],
    "Bills": [
        "rent", "electric", "gas", "water", "council tax", "internet",
        "broadband", "phone bill", "vodafone", "ee", "o2", "three"
    ]
}


def categorise_description(description, amount):
    description = str(description).lower()

    if amount > 0:
        return "Income"

    for category, keywords in CATEGORY_RULES.items():
        for word in keywords:
            if word in description:
                return category

    return "Uncategorised"


def categorise_transactions(df):
    df = df.copy()

    df["Category"] = df.apply(
        lambda row: categorise_description(row["Description"], row["Amount"]),
        axis=1
    )

    return df