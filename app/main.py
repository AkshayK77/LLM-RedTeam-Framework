from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import engine, Base
# Import models so their tables are registered on Base.metadata before create_all
import app.models.job  # noqa: F401
import app.models.result  # noqa: F401
from app.routers import jobs, prompts, reports, classify

app = FastAPI(title="LLM Red-Teaming Framework", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(classify.router, prefix="/classify", tags=["classify"])


@app.get("/")
def root():
    return {"message": "LLM Red-Teaming Framework is running"}
