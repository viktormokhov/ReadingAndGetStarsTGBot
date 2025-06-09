from pydantic import BaseModel


class TelegramValidationRequest(BaseModel):
    initData: str

class TelegramValidationResponse(BaseModel):
    success: bool
    valid: bool