from typing import Any

from sqlalchemy import select, func

from core.content_config import BADGES
from core.database.init_db import AsyncSessionLocal
from core.database.models import ThemeStat, User, Card
from core.database.user_ops import update_user_accuracy


async def accuracy(uid: int, correct: bool):
    """Обновляет статистику точности пользователя."""
    async with AsyncSessionLocal.begin() as session:
        await update_user_accuracy(uid, correct, session)


async def user_summary(uid: int) -> dict[str, Any]:
    """Возвращает статистику пользователя: имя, звезды, карточки, вопросы, точность, серии, темы."""
    async with AsyncSessionLocal() as session:
        user = await session.get(User, uid)
        if not user:
            return {}
        themes = await session.scalars(select(ThemeStat).where(ThemeStat.user_id == uid))
        questions_count = (await session.execute(
            select(func.sum(ThemeStat.texts)).where(ThemeStat.user_id == uid))).scalar() or 0
        card_count = (await session.execute(
            select(func.count()).select_from(Card).where(Card.user_id == uid))).scalar() or 0

        return {
            "name": user.name,
            "stars": user.stars,
            "q_ok": user.q_ok,
            "q_tot": user.q_tot,
            "streak": user.streak,
            "questions_count": questions_count,
            "card_count": card_count,
            "themes": {t.theme: t.texts for t in themes}
        }


def get_status_by_stars(total: int) -> str:
    """Возвращает статус пользователя по количеству звёзд."""
    prev = "🔸 Начинающий"
    for thr in sorted(BADGES):
        if total < thr:
            return prev
        prev = BADGES[thr]
    return prev
