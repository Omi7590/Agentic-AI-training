# RTI Mitra - explore.py
# Prints 3 facts about the RTI rule records using pandas.

import json
import os
import pandas as pd

RECORDS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "records.json"
)

def load_df():
    with open(RECORDS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return pd.DataFrame(data)

def main():
    df = load_df()

    print("=== RTI Mitra - Data Facts ===\n")

    # Fact 1: count by jurisdiction
    print("Fact 1: Number of rules per jurisdiction")
    print(df["jurisdiction"].value_counts().to_string())
    print()

    # Fact 2: rules with a numeric amount or time limit
    has_limit = df[df["amount_or_time_limit"].str.contains(
        r"\d", regex=True, na=False
    )]
    print(f"Fact 2: Records with a numeric amount or time limit: {len(has_limit)}")
    print(has_limit[["topic", "amount_or_time_limit"]].to_string(index=False))
    print()

    # Fact 3: most common words across all rules
    all_text = " ".join(df["rule"].tolist()).lower()
    words = [w.strip(".,()") for w in all_text.split() if len(w) > 4]
    word_series = pd.Series(words).value_counts().head(10)
    print("Fact 3: Top 10 most frequent words in rule text")
    print(word_series.to_string())

if __name__ == "__main__":
    main()
