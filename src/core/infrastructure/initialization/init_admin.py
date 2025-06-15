import logging

from config.settings import get_tg_settings
from core.infrastructure.db.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository

logger = logging.getLogger(__name__)

tg_settings = get_tg_settings()

async def init_admin_flags():
    """
    Проставляет флаг is_admin=True для всех ID администраторов из TG_ADMIN_ID.
    Создаёт пользователей-администраторов в базе, если их нет.
    """
    async with SQLAlchemyUserRepository() as repo:
        admin_id = tg_settings.tg_admin_id
        user = await repo.get_by_id(admin_id)
        if user is None:
            await repo.create(uid=admin_id, name="admin", gender='male', birthdate=None, is_admin=True, status='approved')
            logger.info(f"👤 Пользователь {admin_id} создан как admin")
        elif not user.is_admin:
            user.is_admin = True
            await repo.session.commit()
            logger.info(f"🔑 Пользователь {admin_id} теперь admin")
