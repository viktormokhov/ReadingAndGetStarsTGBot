from abc import ABC, abstractmethod
from typing import Any

class MongoHealthChecker(ABC):
    """
    Абстрактный класс для проверки состояния MongoDB.

    Все реализации должны предоставлять асинхронный метод check.

    Пример реализации:
        class MyMongoHealthChecker(MongoHealthChecker):
            async def check(self, request: Any) -> dict[str, Any]:
                # логика проверки состояния MongoDB
    """
    @abstractmethod
    async def check(self, request: Any) -> dict[str, Any]:
        pass

class RedisHealthChecker(ABC):
    """
    Абстрактный класс для проверки состояния Redis.

    Пример реализации:
        class MyRedisHealthChecker(RedisHealthChecker):
            async def check(self) -> dict[str, Any]:
                # логика проверки состояния Redis
    """
    @abstractmethod
    async def check(self) -> dict[str, Any]:
        pass

class DBHealthChecker(ABC):
    """
    Абстрактный класс для проверки состояния основной базы данных.

    Пример реализации:
        class MyDBHealthChecker(DBHealthChecker):
            async def check(self) -> dict[str, Any]:
                # логика проверки состояния БД
    """
    @abstractmethod
    async def check(self) -> dict[str, Any]:
        pass

class SystemStatusChecker(ABC):
    """
    Абстрактный класс для получения сводной информации о состоянии системы.

    Пример реализации:
        class MySystemStatusProvider(SystemStatusProvider):
            async def get_status(self) -> dict[str, Any]:
                # логика формирования статуса системы
    """
    @abstractmethod
    async def get_status(self) -> dict[str, Any]:
        pass
