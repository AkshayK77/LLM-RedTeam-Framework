# OSB-JailbreakBench

A systematic benchmark of human jailbreak prompt categories against 
current-generation open-source LLMs.

## Models
- Llama 3.1 8B Instruct (Groq)
- Mistral 7B Instruct (Groq)
- Gemma 2 9B Instruct (Groq)
- Mixtral 8x7B Instruct (Groq)

## Attack Categories
1. Roleplay / Persona (DAN variants)
2. Privilege Escalation (Developer Mode)
3. Encoding Tricks (Base64, leetspeak, ROT13)
4. Many-Shot Priming
5. Multilingual (via MultiJail)
6. Narrative / Fictional Framing

## Setup
1. Clone this repo
2. Create a virtual environment: `python -m venv jailbreak-bench`
3. Activate it: `source jailbreak-bench/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Add your API keys to `.env`
6. Run evaluations: `python scripts/run_evaluations.py`

## Structure
- `prompts/` — 90 jailbreak prompts across 6 categories (15 each)
- `scripts/` — evaluation pipeline, judge, ASR computation
- `results/` — raw completions and scores (gitignored)
- `analysis/` — Jupyter notebook for figures and taxonomy
- `data/` — MultiJail dataset samples
