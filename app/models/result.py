from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey
from uuid import uuid4
from app.db import Base


class Result(Base):
    __tablename__ = "results"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    prompt_id = Column(String, nullable=False)
    category = Column(String, nullable=False)
    prompt_text = Column(Text, nullable=False)
    completion = Column(Text, nullable=False)
    judge_score = Column(Integer, nullable=False)
    flagged = Column(Boolean, default=False)
