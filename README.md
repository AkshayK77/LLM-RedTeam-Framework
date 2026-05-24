# LLM Red-Teaming & Jailbreak Detection Framework

An end-to-end framework for benchmarking LLM resistance to adversarial jailbreak attacks. This project extends the [OSB-Bench](https://github.com/AkshayK77/osb-jailbreak-bench) research by wrapping the original evaluation pipeline in a REST API and interactive Streamlit UI, enabling on-demand benchmarking, real-time job tracking, automatic ASR computation, and baseline comparison against published OSB-Bench results — all backed by a SQLite database and served via FastAPI.

## Setup

```bash
git clone <repo-url>
cd llm-redteam-framework
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in the project root and add your Groq API key:

```
GROQ_API_KEY=your_key_here
```

## Running the API

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## Running the Streamlit UI

In a separate terminal (with the API already running):

```bash
streamlit run streamlit_app/app.py
```

The UI will open at `http://localhost:8501`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/jobs` | Submit a new benchmark job (model + categories) |
| `GET` | `/jobs/{id}` | Poll job status; returns ASR table when complete |
| `GET` | `/prompts` | List all prompts grouped by category |
| `GET` | `/prompts/{category}` | List prompts for a single category |
| `GET` | `/reports/{id}` | Full report with baseline comparison for a completed job |

## Models Supported

- `llama-3.1-8b-instant`
- `llama-3.3-70b-versatile`
- `llama-4-scout-17b-16e-instruct`
- `qwen/qwen3-32b`
- `allam-2-7b`
- `openai/gpt-4o-mini`

## OSB-Bench Baseline ASR Values

| Category | Baseline ASR |
|----------|-------------|
| `narrative_fictional` | 32.2% |
| `roleplay_persona` | 21.7% |
| `encoding_tricks` | 16.8% |
| `many_shot` | 8.9% |
| `privilege_escalation` | 6.7% |
| `multilingual` | 1.1% |

## Project Structure

```
llm-redteam-framework/
├── app/                    # FastAPI backend
│   ├── main.py             # App entry point
│   ├── db.py               # SQLAlchemy engine + session
│   ├── routers/            # jobs, prompts, reports endpoints
│   ├── models/             # ORM models + Pydantic schemas
│   └── services/           # execution, classifier, asr, report logic
├── streamlit_app/
│   └── app.py              # Streamlit UI
├── prompts/                # 90 jailbreak prompts (6 categories × 15)
├── scripts/                # Original OSB-Bench evaluation pipeline
├── results/                # Raw completions and scores
├── analysis/               # Jupyter notebook for figures
└── data/                   # MultiJail dataset samples
```
