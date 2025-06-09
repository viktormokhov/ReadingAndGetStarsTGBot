from typing import Optional

from pydantic import BaseModel


class TelegramWebhook(BaseModel):
    callback_query: Optional[dict] = None
    message: Optional[dict] = None