import logging

from config.settings import tg_settings
from core.infrastructure.database.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository

logger = logging.getLogger(__name__)


async def init_admin_flags():
    """
    Проставляет флаг is_admin=True для всех ID администраторов из TG_ADMIN_IDS.
    Создаёт пользователей-администраторов в базе, если их нет.
    """
    async with SQLAlchemyUserRepository() as repo:
        for admin_id in tg_settings.tg_admin_ids:
            user = await repo.get_by_id(admin_id)
            if user is None:
                await repo.create(admin_id, name="admin", is_admin=True, is_approved=True)
                logger.info(f"👤 Пользователь {admin_id} создан как admin")
            elif not user.is_admin:
                user.is_admin = True
                await repo.session.commit()
                logger.info(f"🔑 Пользователь {admin_id} теперь admin")
