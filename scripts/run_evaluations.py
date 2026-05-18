"""
run_evaluations.py
Sends all prompts to all models and saves completions.
"""

import os
import json
import time
from groq import Groq
from dotenv import load_dotenv
from tqdm import tqdm
from datetime import datetime

load_dotenv()

MODELS = {
    "llama-3.1-8b":      "llama-3.1-8b-instant",
    "llama-3.3-70b":     "llama-3.3-70b-versatile",
    "llama-4-scout-17b": "meta-llama/llama-4-scout-17b-16e-instruct",
    "gpt-oss-20b":       "openai/gpt-oss-20b",
    "qwen3-32b":         "qwen/qwen3-32b",
    "allam-2-7b":        "sdaia/allam-2-7b-instruct",
}

MAX_TOKENS = 512
TEMPERATURE = 0
PROMPTS_DIR = "prompts"
RESULTS_DIR = "results/completions"

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def load_all_prompts():
    all_prompts = []
    for filename in os.listdir(PROMPTS_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(PROMPTS_DIR, filename), encoding="utf-8") as f:
                data = json.load(f)
                for p in data["prompts"]:
                    p["category"] = data["category"]
                    all_prompts.append(p)
    return all_prompts

def run_model(model_name, model_id, prompts):
    results = []
    for prompt in tqdm(prompts, desc=f"Running {model_name}"):
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt["text"]}],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            completion = response.choices[0].message.content
        except Exception as e:
            completion = f"ERROR: {str(e)}"

        results.append({
            "prompt_id": prompt["id"],
            "category": prompt["category"],
            "prompt_text": prompt["text"],
            "completion": completion,
            "model": model_name,
            "timestamp": datetime.utcnow().isoformat()
        })
        time.sleep(2)  # Respect rate limits
    return results

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    prompts = load_all_prompts()
    print(f"Loaded {len(prompts)} prompts across all categories")

    for model_name, model_id in MODELS.items():
        output_path = os.path.join(RESULTS_DIR, f"{model_name}.json")
        if os.path.exists(output_path):
            print(f"\nSkipping {model_name} (already exists)")
            continue
        print(f"\nRunning {model_name}...")
        results = run_model(model_name, model_id, prompts)

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Saved {len(results)} completions to {output_path}")

if __name__ == "__main__":
    main()
