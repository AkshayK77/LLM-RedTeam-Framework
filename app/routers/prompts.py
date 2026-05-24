import os
import json
from fastapi import APIRouter, HTTPException
from app.models.schemas import PromptItem

router = APIRouter()

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "prompts")

CATEGORY_FILE_MAP = {
    "roleplay_persona": "roleplay_persona.json",
    "privilege_escalation": "privilege_escalation.json",
    "encoding_tricks": "encoding_tricks.json",
    "many_shot": "many_shot.json",
    "multilingual": "multilingual.json",
    "narrative_fictional": "narrative_fictional.json",
}


def _load_category(category: str) -> list[PromptItem]:
    filename = CATEGORY_FILE_MAP.get(category)
    if not filename:
        return None
    path = os.path.join(PROMPTS_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    prompts = data.get("prompts", [])
    return [
        PromptItem(
            prompt_id=p.get("id", ""),
            category=category,
            text=p.get("text", p.get("prompt", "")),
            harmful_request=p.get("harmful_request", ""),
        )
        for p in prompts
    ]


@router.get("")
def get_all_prompts() -> dict:
    result = {}
    for category in CATEGORY_FILE_MAP:
        items = _load_category(category)
        if items is not None:
            result[category] = [i.model_dump() for i in items]
    return result


@router.get("/{category}")
def get_prompts_by_category(category: str) -> list:
    items = _load_category(category)
    if items is None:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    return [i.model_dump() for i in items]
