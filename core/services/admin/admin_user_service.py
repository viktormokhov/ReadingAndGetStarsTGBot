from typing import List
from sqlalchemy import func
from core.database import user_ops
from core.database.init_db import AsyncSessionLocal
from core.database.models import User
from core.database.user_ops import select_user_card_counts
from core.models.pagination import PageParams
from core.models.user_stat import UserStat

async def fetch_user_stats(page_params: PageParams) -> List[UserStat]:
    async with AsyncSessionLocal() as s:
        users = (await s.execute(user_ops.select_users_where(lambda u: True))).scalars().all()

        # Срезим по странице
        slice_users = users[page_params.offset:page_params.offset+page_params.page_size]

        stats = []
        for u in slice_users:
            cards = await s.scalar(select_user_card_counts(u.id))
            stats.append(UserStat(
                id=u.id,
                name=u.name or "—",
                is_approved=u.is_approved,
                stars=u.stars or 0,
                cards=cards or 0,
                q_ok=u.q_ok or 0,
                q_tot=u.q_tot or 0,
                streak=u.streak or 0
            ))
        total = len(users)
    # Возвращаем статистику + общий размер для навигации
    return stats, total
