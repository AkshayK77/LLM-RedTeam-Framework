"""
populate_multilingual.py
Loads MultiJail dataset (wide format) from HuggingFace, samples 15 prompts
across non-English language columns, and writes to prompts/multilingual.json.

Dataset structure: each row is one harmful prompt translated into all languages.
Columns: id, source, tags, en, zh, it, vi, ar, ko, th, bn, sw, jv
"""

import os
import sys
import json
from datasets import load_dataset
from dotenv import load_dotenv

# Force UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

NON_ENGLISH_LANGS = {
    "zh": "Chinese",
    "it": "Italian",
    "vi": "Vietnamese",
    "ar": "Arabic",
    "ko": "Korean",
    "th": "Thai",
    "bn": "Bengali",
    "sw": "Swahili",
    "jv": "Javanese",
}

# Tags from MultiJail mapped to our scenario schema
SCENARIO_MAP = {
    "illegal_activity": "illegal_activity",
    "hate_speech": "hate_speech",
    "malware": "malware",
    "physical_harm": "physical_harm",
    "fraud": "fraud",
    "disinformation": "disinformation",
    "economic_harm": "fraud",
    "privacy_violation": "illegal_activity",
    "adult_content": "illegal_activity",
    "political_content": "disinformation",
    "harassment": "hate_speech",
}

def tags_to_scenario(tags):
    """Parse the tags list/string and return the best matching scenario."""
    if not tags:
        return "illegal_activity"
    if isinstance(tags, list):
        for tag in tags:
            t = str(tag).lower().replace(" ", "_")
            if t in SCENARIO_MAP:
                return SCENARIO_MAP[t]
        return "illegal_activity"
    # String form
    t = str(tags).lower().replace(" ", "_")
    for key, val in SCENARIO_MAP.items():
        if key in t:
            return val
    return "illegal_activity"

def main():
    print("Loading MultiJail dataset...")
    try:
        ds = load_dataset("DAMO-NLP-SG/MultiJail", token=HF_TOKEN)
    except Exception as e:
        print(f"Token auth failed ({e}), trying public access...")
        ds = load_dataset("DAMO-NLP-SG/MultiJail")

    data = ds["train"]
    print(f"Loaded {len(data)} rows, columns: {data.column_names}")

    rows = [dict(data[i]) for i in range(len(data))]

    # Sample 15 rows spread across non-English languages.
    # Strategy: 2 rows per language for zh/it/vi/ar/ko/th (6 langs × 2 = 12)
    #           1 row per language for bn/sw/jv (3 langs × 1 = 3) → total 15
    lang_quotas = {
        "zh": 2, "it": 2, "vi": 2,
        "ar": 2, "ko": 2, "th": 2,
        "bn": 1, "sw": 1, "jv": 1,
    }

    prompts = []
    prompt_id = 1
    used_row_indices = set()

    for lang_code, quota in lang_quotas.items():
        lang_name = NON_ENGLISH_LANGS[lang_code]
        count = 0
        for idx, row in enumerate(rows):
            if idx in used_row_indices:
                continue
            text = row.get(lang_code, "")
            if not text or not text.strip():
                continue

            scenario = tags_to_scenario(row.get("tags"))
            en_text = row.get("en", "")

            prompts.append({
                "id": f"ml_{prompt_id:03d}",
                "text": text.strip(),
                "harmful_request": en_text.strip()[:120] if en_text else "harmful request",
                "scenario": scenario,
                "language": lang_name,
                "language_code": lang_code,
                "source": "multijail_deng_2024"
            })

            used_row_indices.add(idx)
            prompt_id += 1
            count += 1
            if count >= quota:
                break

        print(f"  {lang_name} ({lang_code}): sampled {count}/{quota}")

    print(f"\nTotal sampled: {len(prompts)} prompts")

    output = {
        "category": "multilingual",
        "description": "Multilingual jailbreaks sampled from MultiJail dataset (Deng et al., ICLR 2024)",
        "prompts": prompts
    }

    out_path = os.path.join("prompts", "multilingual.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Written to {out_path}")
    for p in prompts:
        preview = p["text"][:55].replace("\n", " ")
        print(f"  {p['id']} [{p['language_code']}] {p['scenario']:20s} | {preview}...")

if __name__ == "__main__":
    main()
