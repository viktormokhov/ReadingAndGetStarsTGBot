import logging

from sqlalchemy import text

from core.config import tg_settings
from core.database.models import Base, User
from core.services.clients.sqlalchemy import sqlalchemy_engine, AsyncSessionLocal

logger = logging.getLogger(__name__)


async def init_db():
    """
    Проверяет наличие таблицы users и при отсутствии создаёт все таблицы,
    затем инициализирует админов.
    Логирует статус через logger.
    """
    try:
        async with sqlalchemy_engine.begin() as conn:
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
            )
            if result.first() is None:
                logger.info("🛠️ Таблицы не найдены — создаём...")
                await conn.run_sync(Base.metadata.create_all)
            else:
                logger.info("✅ Таблицы уже существуют.")
    except Exception as e:
        logger.error("❌ Database initialization failed", exc_info=e)
        return  # или можешь вернуть False/None, если нужно

    # инициализируем флаги администраторов
    await init_admin_flags()


async def init_admin_flags():
    """
    Проставляет флаг is_admin=True для всех ID админов из TG_ADMIN_IDS.
    Логирует статус через logger.
    """
    try:
        async with AsyncSessionLocal.begin() as session:
            for admin_id in tg_settings.admin_ids:
                user = await session.get(User, admin_id)
                if user:
                    if not user.is_admin:
                        user.is_admin = True
                        logger.info(f"🔑 Пользователь {admin_id} теперь admin")
                else:
                    session.add(User(
                        id=admin_id,
                        name="admin",
                        is_admin=True,
                        is_approved=True
                    ))
                    logger.info(f"👤 Пользователь {admin_id} создан как admin")
    except Exception as e:
        logger.error("❌ Не удалось проставить флаги admin", exc_info=e)
