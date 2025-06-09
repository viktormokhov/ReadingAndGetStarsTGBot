from src.core.application.interfaces.health_providers import (
    MongoHealthChecker, RedisHealthChecker, DBHealthChecker, SystemStatusChecker
)

class HealthService:
    """
    Сервис для проверки состояния различных компонентов системы.

    Позволяет асинхронно проверять состояние MongoDB, Redis, основной БД и получать статус системы.

    Пример использования:
        health_service = HealthService(mongo_checker, redis_checker, db_checker, sys_provider)
        mongo_status = await health_service.mongo_health(request)
        redis_status = await health_service.redis_health()
        db_status = await health_service.db_health()
        system_status = await health_service.system_status()
    """
    def __init__(
        self,
        mongo_checker: MongoHealthChecker,
        redis_checker: RedisHealthChecker,
        db_checker: DBHealthChecker,
        system_checker: SystemStatusChecker
    ):
        self.mongo_checker = mongo_checker
        self.redis_checker = redis_checker
        self.db_checker = db_checker
        self.system_checker = system_checker

    async def mongo_health(self, request):
        """
        Проверяет состояние MongoDB.

        :param request: Запрос или параметры, необходимые для проверки.
        :return: Словарь с результатом проверки здоровья MongoDB.
        :raises Exception: Если произошла ошибка при проверке.
        """
        return await self.mongo_checker.check(request)

    async def redis_health(self):
        """
        Проверяет состояние Redis.

        :return: Словарь с результатом проверки здоровья Redis.
        :raises Exception: Если произошла ошибка при проверке.
        """
        return await self.redis_checker.check()

    async def db_health(self):
        """
        Проверяет состояние основной базы данных.

        :return: Словарь с результатом проверки здоровья базы данных.
        :raises Exception: Если произошла ошибка при проверке.
        """
        return await self.db_checker.check()

    async def system_status(self):
        """
        Получает общий статус системы.

        :return: Словарь с информацией о состоянии системы.
        :raises Exception: Если произошла ошибка при получении статуса.
        """
        return await self.system_checker.get_status()