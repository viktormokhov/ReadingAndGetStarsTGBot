from typing import Any

from core.application.interfaces.health_providers import RedisHealthChecker


class DefaultRedisHealthChecker(RedisHealthChecker):
    """
    Стандартная асинхронная реализация проверки состояния Redis.

    Выполняет пинг, собирает основную информацию о сервере и считает ключи с заданным префиксом.
    """
    def __init__(self, redis_client):
        self.redis = redis_client

    async def check(self) -> dict[str, Any]:
        pong: bool = await self.redis.ping()
        if not pong:
            raise Exception("Redis is not responding")

        info: dict[str, Any] = await self.redis.info()
        connected_clients: int = int(info.get("connected_clients", 0))
        version: str | None = info.get("redis_version")
        uptime: int = int(info.get("uptime_in_seconds", 0))
        used_memory: int = int(info.get("used_memory", 0))
        used_memory_mb: float = round(used_memory / (1024 * 1024), 2)
        total_keys: int = await self.count_keys_with_prefix(self.redis, prefix="user")

        # Оптимизация: получение host/port напрямую из connection_kwargs (это словарь, а не объект)
        host: Any = self.redis.connection_pool.connection_kwargs.get("host", None)
        port: Any = self.redis.connection_pool.connection_kwargs.get("port", None)

        return {
            "redis": "OK",
            "status": "Redis is healthy",
            "host": host,
            "port": port,
            "version": version,
            "uptime": uptime,
            "connected_clients": connected_clients,
            "used_memory_mb": used_memory_mb,
            "total_keys": total_keys,
        }

    async def count_keys_with_prefix(self, redis_c: Any, prefix: str) -> int:
        """
        Считает количество ключей в Redis по заданному префиксу.

        :param redis_c: Клиент Redis (ожидается совместимость с aioredis/pure python).
        :param prefix: Префикс ключей (например, 'user').
        :return: Количество найденных ключей.
        """
        cursor: Any = 0  # С aioredis >= 2.0 это int, а не bytes
        count: int = 0
        pattern: str = f"{prefix}*"
        while True:
            cursor, keys = await redis_c.scan(cursor=cursor, match=pattern, count=500)
            count += len(keys)
            if not cursor or cursor == 0 or cursor == b'0':
                break
        return count
