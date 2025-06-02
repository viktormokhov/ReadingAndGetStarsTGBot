from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncEngine

from config.settings import get_db_settings

db_settings = get_db_settings()

sqlalchemy_engine: AsyncEngine = create_async_engine(
    db_settings.db_url,
    echo=False,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=sqlalchemy_engine,
    expire_on_commit=False
)


async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
