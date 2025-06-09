from typing import Any

from core.application.interfaces.health_providers import MongoHealthChecker


class DefaultMongoHealthChecker(MongoHealthChecker):
    """
    Стандартная асинхронная реализация проверки состояния MongoDB.

    Проверяет подключение к MongoDB, получает информацию о сервере,
    список баз данных, общее количество коллекций и общий объём занимаемого места.
    """
    async def check(self, request: Any) -> dict[str, Any]:
        db = request.app.state.db
        mongo_client = request.app.state.mongo_client

        await db.command("ping")

        # Получение информации о сервере и статусе
        server_info = await db.command("buildInfo")
        server_status = await db.command("serverStatus")
        uptime: float | None = server_status.get("uptime")

        # Получение списка баз данных
        dbs_info = await (await mongo_client.list_databases()).to_list(length=None)

        total_collections = 0
        total_storage_bytes = 0
        databases: list[dict[str, Any]] = []

        for dbi in dbs_info:
            size_on_disk = dbi.get("sizeOnDisk", 0)
            databases.append({
                "name": dbi["name"],
                "sizeOnDisk": size_on_disk,
                "empty": dbi.get("empty", False)
            })
            total_storage_bytes += size_on_disk

            # Получение количества коллекций в базе
            db_obj = mongo_client[dbi["name"]]
            coll_names = await db_obj.list_collection_names()
            total_collections += len(coll_names)

        total_storage_mb: float = round(total_storage_bytes / (1024 * 1024), 2) if total_storage_bytes else 0.0

        return {
            "mongo": "OK",
            "status": "MongoDB is healthy",
            "host": getattr(mongo_client, "HOST", None),
            "port": getattr(mongo_client, "PORT", None),
            "server_info": {
                "version": server_info.get("version"),
                "gitVersion": server_info.get("gitVersion"),
                "sysInfo": server_info.get("sysInfo")
            },
            "uptime": uptime,
            "databases": databases,
            "total_collections": total_collections,
            "total_storage_mb": total_storage_mb,
        }