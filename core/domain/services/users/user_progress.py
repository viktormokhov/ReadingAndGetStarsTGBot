from typing import Any

from config.content import BADGES
from core.infrastructure.database.connection import AsyncSessionLocal
from core.infrastructure.database.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from core.infrastructure.database.user_ops import update_user_accuracy


async def accuracy(uid: int, correct: bool):
    """Обновляет статистику точности пользователя."""
    async with AsyncSessionLocal.begin() as session:
        await update_user_accuracy(uid, correct, session)


async def user_summary(uid: int) -> dict[str, Any]:
    """Возвращает статистику пользователя: имя, звезды, карточки, вопросы, точность, серии, темы."""
    async with SQLAlchemyUserRepository() as repo:
        user = await repo.get_by_id(uid)
        if not user:
            return {}

        themes = await repo.get_theme_by_user(uid)
        questions_count = await repo.get_questions_count_by_user(uid)
        card_count = await repo.get_card_count_by_user(uid)
        stars_count = await repo.get_stars_count_by_user(uid)

    return {
        "name": user.name,
        "stars": stars_count,
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
