from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime

from app.db import get_db
from app.models.job import Job
from app.models.schemas import JobCreate, JobResponse
from app.services.execution import run_job
from app.services.asr import compute_asr

router = APIRouter()


@router.post("")
def create_job(body: JobCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    job = Job(
        id=str(uuid4()),
        model_id=body.model_id,
        categories=body.categories,
        status="pending",
        created_at=datetime.utcnow(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(run_job, job.id)

    return {"job_id": job.id, "status": "pending"}


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    asr_table = None
    if job.status == "complete":
        asr_table = compute_asr(job_id)

    return JobResponse(
        id=job.id,
        model_id=job.model_id,
        categories=job.categories,
        status=job.status,
        created_at=job.created_at,
        completed_at=job.completed_at,
        asr_table=asr_table,
    )
