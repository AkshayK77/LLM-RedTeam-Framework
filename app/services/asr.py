from app.db import SessionLocal
from app.models.result import Result


def compute_asr(job_id: str) -> dict:
    """Returns {category: asr_float} for all results of a job."""
    db = SessionLocal()
    try:
        results = db.query(Result).filter(Result.job_id == job_id).all()

        category_scores: dict[str, list[int]] = {}
        for r in results:
            category_scores.setdefault(r.category, []).append(r.judge_score)

        return {
            category: sum(scores) / len(scores) if scores else 0.0
            for category, scores in category_scores.items()
        }
    finally:
        db.close()
