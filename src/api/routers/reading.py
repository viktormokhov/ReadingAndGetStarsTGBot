from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from core.domain.services.ai.llm_text_content_generator import LLMTextContentGenerator
from core.infrastructure.db.connection import AsyncSessionLocal
from core.infrastructure.db import text_log
from config.constants import DAILY_LIMIT_PER_THEME

router = APIRouter(
    prefix="/reading",
    tags=["reading"],
    responses={404: {"description": "Not found"}},
)

class ReadingRequest(BaseModel):
    user_id: int
    category: str
    theme: str

class ReadingResponse(BaseModel):
    text: str
    questions: List[Dict[str, Any]]
    card_title: str
    word_count: int

@router.post("/generate", response_model=ReadingResponse)
async def generate_reading_content(request: ReadingRequest):
    """
    Generate reading content with questions for a specific users, category, and theme.
    This endpoint is for external calls only.
    """
    async with AsyncSessionLocal.begin() as session:
        # Check if users has exceeded daily limit
        count = await text_log.count_generated_today(session, request.user_id, request.theme)
        if count >= DAILY_LIMIT_PER_THEME:
            raise HTTPException(
                status_code=429, 
                detail=f"Daily limit of {DAILY_LIMIT_PER_THEME} generations per theme exceeded"
            )
        
        # Get users age
        age = await get_user_age(request.user_id, session)
    
    # Generate content
    generator = LLMTextContentGenerator(
        uid=request.user_id,
        theme=request.theme,
        age=age
    )
    
    try:
        content = await generator.generate_text(request.category)
        
        return ReadingResponse(
            text=content["text"],
            questions=content["qa"],
            card_title=content["card"],
            word_count=len(content["text"].split())
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating content: {str(e)}")

class CheckLimitRequest(BaseModel):
    user_id: int
    theme: str

class LimitResponse(BaseModel):
    limit_exceeded: bool
    current_count: int
    max_limit: int

@router.post("/check-limit", response_model=LimitResponse)
async def check_daily_limit(request: CheckLimitRequest):
    """
    Check if a users has exceeded their daily limit for a specific theme.
    This endpoint is for external calls only.
    """
    async with AsyncSessionLocal.begin() as session:
        count = await text_log.count_generated_today(session, request.user_id, request.theme)
        
        return LimitResponse(
            limit_exceeded=count >= DAILY_LIMIT_PER_THEME,
            current_count=count,
            max_limit=DAILY_LIMIT_PER_THEME
        )