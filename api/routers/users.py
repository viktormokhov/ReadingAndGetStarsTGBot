from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import select
from api.service.quiz_stats import calculate_user_stats
from core.infrastructure.database.connection import AsyncSessionLocal

from core.application.models.api.quiz import UserQuizCreate, UserQuizResponse, UserStarsResponse
from core.infrastructure.database.models import UserQuizzes
from core.infrastructure.database.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository

router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
    # dependencies=[Depends(verify_api_key)],
    responses={404: {"description": "Not found"}},
)


class UserCreate(BaseModel):
    user_id: int
    name: str


class UserResponse(BaseModel):
    id: int
    name: str
    is_admin: bool
    age: Optional[int] = None
    stars: int = 0
    total_questions: int = 0
    card_count: int = 0


class UserAgeUpdate(BaseModel):
    user_id: int
    age: int


class UserStarsUpdate(BaseModel):
    user_id: int
    stars: int


class UserStatsResponse(BaseModel):
    success: bool
    data: dict
    warning: str | None


# class UserQuizCreate(BaseModel):
#     user_id: int
#     title: str
#     description: Optional[str] = None

@router.get("/{user_id}/statistics", response_model=UserStatsResponse)
async def get_user_stats(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(UserQuizzes).where(UserQuizzes.user_id == user_id)
        )
        user_quizzes = result.scalars().all()
        stats = calculate_user_stats(user_quizzes)
        warning = None if stats["totalQuizzes"] > 0 else "Используются локальные данные"
        return {
            "success": True,
            "data": stats,
            "warning": warning,
        }


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_info(user_id: int):
    """
    Get user information by ID
    This endpoint is for external calls only.
    """
    async with SQLAlchemyUserRepository() as repo:
        user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with ID {user_id} not found"
        )

    stars = await repo.get_stars_count_by_user(user_id)
    total_questions = await repo.get_questions_count_by_user(user_id)
    card_count = await repo.get_card_count_by_user(user_id)

    return UserResponse(
        id=user.id,
        name=user.name,
        is_admin=user.is_admin,
        age=user.age,
        stars=stars,
        total_questions=total_questions,
        card_count=card_count
    )


@router.patch("/{user_id}/update-stars", response_model=UserStarsResponse)
async def update_stars(update_data: UserStarsUpdate):
    """
    Update user stars by adding the specified number of stars.
    This endpoint is for external calls only.
    """
    async with SQLAlchemyUserRepository() as repo:
        user = await repo.get_by_id(update_data.user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with ID {update_data.user_id} not found"
        )

    async with AsyncSessionLocal() as session:
        async with session.begin():
            stars = await add_user_stars(update_data.user_id, update_data.stars, session)
            # total_questions = await get_total_questions(update_data.user_id, session)
            # card_count = await get_user_card_count(update_data.user_id, session)

    return UserStarsResponse(
        user_id=update_data.user_id,
        stars=stars.count,
        updated_at=stars.updated_at,
    )


@router.post("/quiz-result", response_model=UserQuizResponse, status_code=201)
async def add_quiz_result(quiz_data: UserQuizCreate):
    """
    Add a quiz result for a user.
    This endpoint is for external calls only.
    """
    user = await get_user(quiz_data.user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with ID {quiz_data.user_id} not found"
        )

    async with AsyncSessionLocal.begin() as session:
        quiz_data_dict = quiz_data.quiz_data.model_dump(exclude={'questions_details'})
        quiz = await add_user_quiz(
            user_id=quiz_data.user_id,
            quiz_data=quiz_data_dict,
            session=session
        )

        quiz_history_collection=Depends(get_quiz_history_collection)

        await quiz_history_collection.insert_one({
            "user_id": quiz_data.user_id,
            "quiz_id": quiz.id,  # Важно! Получите quiz.id после коммита, чтобы связать документы
            "questions_details": quiz_data.quiz_data.model_dump(include={'questions_details'}),
            "timestamp": datetime.now()
        })

    return UserQuizResponse(
        id=quiz.id,
        user_id=quiz.user_id,
        created_at=quiz.created_at,
    )
