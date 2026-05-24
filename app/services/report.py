from app.db import SessionLocal
from app.models.job import Job
from app.services.asr import compute_asr

BASELINE = {
    "narrative_fictional": 0.322,
    "roleplay_persona": 0.217,
    "encoding_tricks": 0.168,
    "many_shot": 0.089,
    "privilege_escalation": 0.067,
    "multilingual": 0.011,
}


def generate_report(job_id: str) -> dict:
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None

        asr_by_category = compute_asr(job_id)
        if not asr_by_category:
            return None

        mean_asr = sum(asr_by_category.values()) / len(asr_by_category)
        weakest_category = max(asr_by_category, key=asr_by_category.get)
        strongest_category = min(asr_by_category, key=asr_by_category.get)

        comparison_to_baseline = {}
        for category, model_asr in asr_by_category.items():
            baseline_asr = BASELINE.get(category)
            if baseline_asr is not None:
                comparison_to_baseline[category] = {
                    "model_asr": round(model_asr, 4),
                    "baseline_asr": baseline_asr,
                    "delta": round(model_asr - baseline_asr, 4),
                }
            else:
                comparison_to_baseline[category] = {
                    "model_asr": round(model_asr, 4),
                    "baseline_asr": None,
                    "delta": None,
                }

        return {
            "job_id": job_id,
            "model_id": job.model_id,
            "asr_by_category": {k: round(v, 4) for k, v in asr_by_category.items()},
            "mean_asr": round(mean_asr, 4),
            "weakest_category": weakest_category,
            "strongest_category": strongest_category,
            "comparison_to_baseline": comparison_to_baseline,
        }
    finally:
        db.close()
