from typing import List, Tuple

from core.domain.models.pagination import PageParams
from core.domain.models.stats import UserStat
from core.infrastructure.db.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository


async def fetch_user_stats(page_params: PageParams) -> Tuple[List[UserStat], int]:
    async with SQLAlchemyUserRepository() as repo:
        users = repo.get_all()
        slice_users = users[page_params.offset:page_params.offset + page_params.page_size]

        stats = []
        for user in slice_users:
            cards = await repo.get_card_count_by_user(user.id)
            stars = await repo.get_stars_count_by_user(user.id)
            stats.append(UserStat(
                id=user.id,
                name=user.name or "—",
                is_approved=user.is_approved,
                stars=stars,
                cards=cards or 0,
                q_ok=user.q_ok or 0,
                q_tot=user.q_tot or 0,
                streak=user.streak or 0
            ))
        total = len(users)
    # Возвращаем статистику + общий размер для навигации
    return stats, total
