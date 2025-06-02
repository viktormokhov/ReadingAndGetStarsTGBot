import time

import psutil
from sqlalchemy import text

from core.infrastructure.clients.redis_client import rc
from core.infrastructure.database.connection import sqlalchemy_engine

START_TIME = time.time()


# --- MongoDB ---
async def check_mongo_health(request):
    db = request.app.state.db
    mongo_client = request.app.state.mongo_client

    await db.command("ping")
    server_info = await db.command("buildInfo")
    server_status = await db.command("serverStatus")
    uptime = server_status.get("uptime", None)

    dbs_cursor = await mongo_client.list_databases()
    dbs_info = await dbs_cursor.to_list(length=None)
    total_collections = 0
    total_storage_bytes = 0
    databases = []
    for dbi in dbs_info:
        databases.append({
            "name": dbi["name"],
            "sizeOnDisk": dbi.get("sizeOnDisk", 0),
            "empty": dbi.get("empty", False)
        })
        total_storage_bytes += dbi.get("sizeOnDisk", 0)
        db_obj = mongo_client[dbi["name"]]
        coll_names = await db_obj.list_collection_names()
        total_collections += len(coll_names)

    total_storage_mb = round(total_storage_bytes / (1024 * 1024), 2) if total_storage_bytes else 0

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


# --- Redis ---
async def check_redis_health():
    pong = await rc.ping()
    if pong:
        info = await rc.info()
        connected_clients = int(info.get("connected_clients", 0))
        version = info.get("redis_version")
        uptime = int(info.get("uptime_in_seconds", 0))
        used_memory = int(info.get("used_memory", 0))
        used_memory_mb = round(used_memory / (1024 * 1024), 2)
        total_keys = await count_keys_with_prefix(rc, prefix="user")
        host = getattr(rc.connection_pool.connection_kwargs, "host", None)
        port = getattr(rc.connection_pool.connection_kwargs, "port", None)

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
    else:
        raise Exception("Redis is not responding")


async def count_keys_with_prefix(redis_c, prefix):
    cursor = b'0'
    count = 0
    pattern = f"{prefix}*"
    while cursor:
        cursor, keys = await redis_c.scan(cursor=cursor, match=pattern, count=500)
        count += len(keys)
        if cursor == 0 or cursor == b'0':
            break
    return count


# --- Database ---
async def check_db_health():
    """
    Проверяет состояние базы данных.
    Возвращает словарь с информацией о статусе, версии, аптайме, количестве таблиц, имени базы и типе СУБД.
    """
    async with sqlalchemy_engine.begin() as conn:
        # Проверка соединения
        await conn.execute(text("SELECT 1"))

        # Получаем тип базы из движка (например: "postgresql", "mysql" и т.д.)
        database_type = sqlalchemy_engine.dialect.name

        # Имя базы данных
        result = await conn.execute(text("SELECT current_database()"))
        database_name = result.scalar()

        # Аптайм сервера (только для PostgreSQL)
        result = await conn.execute(text("""
                                         SELECT now() - pg_postmaster_start_time() as uptime
                                         FROM pg_postmaster_start_time();
                                         """))
        uptime = str(result.scalar())

        # Версия сервера
        result = await conn.execute(text("SHOW server_version;"))
        server_version = result.scalar()

        # Количество таблиц в схеме public
        result = await conn.execute(
            text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
        )
        tables_count = result.scalar()

        return {
            "database_type": database_type,  # Теперь определяется автоматически
            "status": "Database is healthy",
            "server_version": server_version,
            "database_name": database_name,
            "uptime": uptime,
            "tables_count": tables_count,
        }


def format_uptime(seconds: int) -> str:
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{days}d {hours}h {minutes}m {seconds}s"


async def get_summary_status():
    # Аптайм приложения
    app_uptime_seconds = int(time.time() - START_TIME)
    app_uptime = format_uptime(app_uptime_seconds)

    # Аптайм сервера (ОС)
    boot_time = psutil.boot_time()
    server_uptime_seconds = int(time.time() - boot_time)
    server_uptime = format_uptime(server_uptime_seconds)

    # Диск (по корневому разделу '/')
    disk = psutil.disk_usage('/')
    disk_total_gb = round(disk.total / (1024 ** 3), 2)
    disk_used_gb = round(disk.used / (1024 ** 3), 2)
    disk_free_gb = round(disk.free / (1024 ** 3), 2)
    disk_percent = disk.percent

    # Оперативная память
    mem = psutil.virtual_memory()
    mem_total_gb = round(mem.total / (1024 ** 3), 2)
    mem_used_gb = round(mem.used / (1024 ** 3), 2)
    mem_free_gb = round(mem.available / (1024 ** 3), 2)
    mem_percent = mem.percent

    # CPU
    cpu_percent = psutil.cpu_percent(interval=0.2)

    return {
        "status": "ok",
        "app_uptime_seconds": app_uptime_seconds,
        "app_uptime": app_uptime,
        "server_uptime_seconds": server_uptime_seconds,
        "server_uptime": server_uptime,
        "disk": {
            "total_gb": disk_total_gb,
            "used_gb": disk_used_gb,
            "free_gb": disk_free_gb,
            "usage_percent": disk_percent
        },
        "memory": {
            "total_gb": mem_total_gb,
            "used_gb": mem_used_gb,
            "free_gb": mem_free_gb,
            "usage_percent": mem_percent
        },
        "cpu": {
            "usage_percent": cpu_percent
        }
    }