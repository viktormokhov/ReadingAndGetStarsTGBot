from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

class QuestionDetail(BaseModel):
    question_id: int
    question_text: str
    is_correct: bool
    user_answer: Optional[str] = None
    correct_answer: Optional[str] = None
    time_spent: Optional[float] = None


class QuizData(BaseModel):
    quiz_id: int
    title: str
    category: str
    difficulty: str
    total_questions: int
    correct_answers: int
    percentage: float
    stars_earned: int
    completed_at: datetime
    time_spent_seconds: int
    hints_used: dict
    generated_by: str
    questions_details: List[QuestionDetail]


class UserQuizCreate(BaseModel):
    user_id: int
    quiz_data: QuizData


class UserQuizResponse(BaseModel):
    id: int                        # id записи, auto-generated
    user_id: int
    created_at: datetime           # когда создана запись


class UserStarsResponse(BaseModel):
    user_id: int
    stars: int
    updated_at: datetime
