from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db import get_db
from app.models.job import Job
from app.models.schemas import ReportResponse
from app.services.report import generate_report

router = APIRouter()


@router.get("/{job_id}", response_model=ReportResponse)
def get_report(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "complete":
        raise HTTPException(status_code=400, detail=f"Job is not complete (status: {job.status})")

    report = generate_report(job_id)
    if not report:
        raise HTTPException(status_code=500, detail="Failed to generate report")

    return ReportResponse(**report)
