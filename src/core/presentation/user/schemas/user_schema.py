from typing import Optional

from pydantic import BaseModel, Field

from core.domain.models.user import Gender


class GenerateAvatarRequest(BaseModel):
    user_id: int
    prompt: str

class GenerateAvatarResponse(BaseModel):
    success: bool
    avatar_url: Optional[str] = None
    avatar_uuid: Optional[str] = None
    # attempts_count: Optional[int] = None
    error: Optional[str] = None

class RegistrationRequest(BaseModel):
    telegram_id: int = Field(..., alias="telegramId")
    name: str
    birth_date: str = Field(..., alias="birthDate")
    gender: Gender
    avatar: str
    init_data: str = Field(..., alias="initData")
