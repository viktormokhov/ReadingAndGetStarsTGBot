# --- Database ---
from typing import Any

from sqlalchemy import text

from core.application.interfaces.health_providers import DBHealthChecker
from core.infrastructure.database.connection import sqlalchemy_engine


class DefaultDBHealthChecker(DBHealthChecker):
    """
    Стандартная асинхронная реализация health-check для PostgreSQL.

    Позволяет проверить соединение, версию сервера, аптайм, количество таблиц, имя базы и тип СУБД.
    """
    async def check(self) -> dict[str, Any]:
        async with sqlalchemy_engine.begin() as conn:
            # Проверка соединения
            await conn.execute(text("SELECT 1"))

            # Определяем тип базы данных из движка
            database_type: str = sqlalchemy_engine.dialect.name

            # Имя базы данных
            result = await conn.execute(text("SELECT current_database()"))
            database_name = result.scalar()

            # Аптайм сервера
            uptime: str | None = None
            if database_type == "postgresql":
                result = await conn.execute(
                    text(
                        "SELECT now() - pg_postmaster_start_time() as uptime "
                        "FROM pg_postmaster_start_time();"
                    )
                )
                uptime = str(result.scalar())

            # Версия сервера
            result = await conn.execute(text("SHOW server_version;"))
            server_version = result.scalar()

            # Количество таблиц в схеме public
            tables_count: int = 0
            result = await conn.execute(
                text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
            )
            tables_count = result.scalar()

            return {
                "database_type": database_type,
                "status": "Database is healthy",
                "server_version": server_version,
                "database_name": database_name,
                "uptime": uptime,
                "tables_count": tables_count,
            }
