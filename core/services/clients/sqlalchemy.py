from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine

from core.config import db_settings

sqlalchemy_engine: AsyncEngine = create_async_engine(db_settings.db_url, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(bind=sqlalchemy_engine, expire_on_commit=False)