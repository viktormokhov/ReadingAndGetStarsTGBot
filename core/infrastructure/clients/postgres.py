import logging

import asyncpg

from config.settings import get_db_settings, DBSettings
from core.infrastructure.database.connection import sqlalchemy_engine
from core.infrastructure.database.models import Base
from core.infrastructure.initialization.init_admin import init_admin_flags

logger = logging.getLogger(__name__)


async def create_database_if_not_exists(db_settings: DBSettings):
    try:
        conn = await asyncpg.connect(
            user=db_settings.postgres_user,
            password=db_settings.secret,
            host=db_settings.postgres_host,
            port=db_settings.postgres_port,
            database='postgres',
        )
        db_name = db_settings.postgres_db_name
        exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", db_name)
        if not exists:
            await conn.execute(f'CREATE DATABASE "{db_name}"')
            logging.info(f"✅ Database '{db_name}' was created successfully.")
        else:
            logging.info(f"🟡 Database '{db_name}' already exists. Creation skipped.")
        await conn.close()
    except Exception as e:
        logging.error(f"❌ Failed to create database '{db_name}': {e}")
        raise


async def init_db():
    """Создаёт все таблицы при необходимости и инициализирует администраторов."""
    db_settings = get_db_settings()
    try:
        await create_database_if_not_exists(db_settings)
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
