from typing import Optional

from pydantic import BaseModel, Field


class GenerateAvatarRequest(BaseModel):
    user_id: int
    prompt: str

    class Config:
        allow_population_by_field_name = True

class GenerateAvatarResponse(BaseModel):
    success: bool
    avatar_url: Optional[str] = None
    avatar_uuid: Optional[str] = None
    # attempts_count: Optional[int] = None
    error: Optional[str] = None
