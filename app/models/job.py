from sqlalchemy import Column, String, DateTime, JSON
from datetime import datetime
from uuid import uuid4
from app.db import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    model_id = Column(String, nullable=False)
    categories = Column(JSON, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
