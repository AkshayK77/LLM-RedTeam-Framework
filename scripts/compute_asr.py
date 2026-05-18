"""
compute_asr.py
Aggregates scored results into ASR tables by model and category.
"""

import os
import json
import pandas as pd

def load_scores():
    scores_dir = "results/scores"
    all_scores = []
    for filename in os.listdir(scores_dir):
        if filename.endswith("_scored.json"):
            with open(os.path.join(scores_dir, filename)) as f:
                all_scores.extend(json.load(f))
    return pd.DataFrame(all_scores)

def compute_asr(df):
    df = df[df["binary_score"].notna()]
    asr_table = df.groupby(["model", "category"])["binary_score"].mean().unstack()
    asr_table = asr_table.round(3)
    return asr_table

def main():
    df = load_scores()
    asr_table = compute_asr(df)

    print("\n=== ASR by Model and Category ===")
    print(asr_table.to_string())

    asr_table.to_csv("results/asr_table.csv")
    print("\nSaved to results/asr_table.csv")

if __name__ == "__main__":
    main()
