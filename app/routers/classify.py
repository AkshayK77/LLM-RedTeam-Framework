from fastapi import APIRouter
from pydantic import BaseModel
from app.services.classifier import classify

router = APIRouter()


class ClassifyRequest(BaseModel):
    prompt_text: str
    completion: str


@router.post("")
def classify_completion(body: ClassifyRequest):
    return classify(body.prompt_text, body.completion)
