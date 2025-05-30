import logging

from core.infrastructure.database.connection import sqlalchemy_engine
from core.infrastructure.database.models import Base
from core.infrastructure.initialization.init_admin import init_admin_flags

logger = logging.getLogger(__name__)


async def init_db():
    """Создаёт все таблицы при необходимости и инициализирует администраторов."""
    try:
        async with sqlalchemy_engine.begin() as conn:
            # Создаст только недостающие таблицы
            await conn.run_sync(Base.metadata.create_all)
        logging.info("✅ SQLAlchemy initialization completed")
    except Exception as e:
        logger.error("❌ Database initialization error", exc_info=e)
        raise

    try:
        await init_admin_flags()
    except Exception as e:
        logger.error("❌ Failed to initialize administrators", exc_info=e)
        raise
