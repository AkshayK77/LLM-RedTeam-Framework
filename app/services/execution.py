import os
import json
import time
from datetime import datetime
from uuid import uuid4
from groq import Groq
from dotenv import load_dotenv

from app.db import SessionLocal
from app.models.job import Job
from app.models.result import Result
from app.services.classifier import classify

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "prompts")

CATEGORY_FILE_MAP = {
    "roleplay_persona": "roleplay_persona.json",
    "privilege_escalation": "privilege_escalation.json",
    "encoding_tricks": "encoding_tricks.json",
    "many_shot": "many_shot.json",
    "multilingual": "multilingual.json",
    "narrative_fictional": "narrative_fictional.json",
}


def _load_prompts(category: str) -> list[dict]:
    filename = CATEGORY_FILE_MAP.get(category)
    if not filename:
        return []
    path = os.path.join(PROMPTS_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    # Each file has a top-level "prompts" list
    return data.get("prompts", [])


def _get_completion(model_id: str, prompt_text: str) -> str:
    for attempt in range(6):
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt_text}],
                max_tokens=512,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            err = str(e)
            if "429" in err:
                wait = 30 * (2 ** attempt)
                time.sleep(wait)
            else:
                return f"ERROR: {err}"
    return "ERROR: Max retries exceeded"


def run_job(job_id: str):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return

        job.status = "running"
        db.commit()

        for category in job.categories:
            prompts = _load_prompts(category)
            for prompt in prompts:
                prompt_id = prompt.get("id", str(uuid4()))
                prompt_text = prompt.get("text", prompt.get("prompt", ""))

                completion = _get_completion(job.model_id, prompt_text)
                time.sleep(2)  # Avoid rate limits between completions

                verdict = classify(prompt_text, completion)

                result = Result(
                    id=str(uuid4()),
                    job_id=job_id,
                    prompt_id=prompt_id,
                    category=category,
                    prompt_text=prompt_text,
                    completion=completion,
                    judge_score=verdict["score"],
                    flagged=verdict["flagged"],
                )
                db.add(result)
                db.commit()

        job.status = "complete"
        job.completed_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        db.rollback()
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = "failed"
            db.commit()
    finally:
        db.close()
