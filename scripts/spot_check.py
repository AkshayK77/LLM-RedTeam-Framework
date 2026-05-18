"""
spot_check.py
Randomly samples 10% of completions for manual human labeling.
Outputs a CSV for easy review.
"""

import os
import json
import pandas as pd
import random

def main():
    scores_dir = "results/scores"
    all_scored = []

    for filename in os.listdir(scores_dir):
        if filename.endswith("_scored.json"):
            with open(os.path.join(scores_dir, filename)) as f:
                all_scored.extend(json.load(f))

    total = len(all_scored)
    sample_size = max(1, int(total * 0.10))
    sample = random.sample(all_scored, sample_size)

    df = pd.DataFrame(sample)[[
        "prompt_id", "category", "model",
        "prompt_text", "completion",
        "binary_score", "graded_score", "reason"
    ]]
    df["human_binary"] = ""
    df["human_graded"] = ""
    df["human_notes"] = ""

    output_path = "results/spot_check_sample.csv"
    df.to_csv(output_path, index=False)
    print(f"Spot check sample ({sample_size} items) saved to {output_path}")
    print("Fill in human_binary, human_graded, human_notes columns manually.")

if __name__ == "__main__":
    main()
