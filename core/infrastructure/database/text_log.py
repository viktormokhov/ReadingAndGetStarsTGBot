from .models import TextGeneration
from datetime import date
from sqlalchemy import select, func


async def log_text_generation(session, user_id: int, theme: str):
    session.add(TextGeneration(user_id=user_id, theme=theme))
    await session.commit()
