from .models import TextGeneration
from datetime import date
from sqlalchemy import select, func


async def log_text_generation(session, user_id: int, theme: str):
    session.add(TextGeneration(user_id=user_id, theme=theme))
    await session.commit()


async def count_generated_today(session, user_id: int, theme: str) -> int:
    today = date.today()
    stmt = select(func.count()).select_from(TextGeneration).where(
        TextGeneration.user_id == user_id,
        TextGeneration.theme == theme,
        func.date(TextGeneration.created_at) == today
    )
    result = await session.execute(stmt)
    return result.scalar()
