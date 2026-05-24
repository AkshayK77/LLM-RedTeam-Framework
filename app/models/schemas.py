from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class JobCreate(BaseModel):
    model_config = {"protected_namespaces": ()}

    model_id: str
    categories: list[str]


class JobResponse(BaseModel):
    model_config = {"from_attributes": True, "protected_namespaces": ()}

    id: str
    model_id: str
    categories: list[str]
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    asr_table: Optional[dict] = None


class PromptItem(BaseModel):
    prompt_id: str
    category: str
    text: str
    harmful_request: str = ""


class ReportResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    job_id: str
    model_id: str
    asr_by_category: dict
    mean_asr: float
    weakest_category: str
    strongest_category: str
    comparison_to_baseline: dict
