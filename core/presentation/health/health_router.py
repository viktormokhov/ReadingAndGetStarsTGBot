from typing import Any

from fastapi import APIRouter, Request, status, Depends
from starlette.responses import JSONResponse

from core.application.services.health_service import HealthService
from core.presentation.deps import verify_api_key, get_health_service
from core.presentation.health.schemas.response_health import (
    MongoHealthResponse,
    RedisHealthResponse,
    DBHealthResponse,
    HealthStatusResponse,
    HealthCheckResponse,
)

router = APIRouter(
    prefix="/api/v1/health",
    tags=["health"],
    dependencies=[Depends(verify_api_key)],
    responses={404: {"description": "Not found"}},
)


@router.get("/check",
            summary="Health check",
            response_model=HealthCheckResponse,
            response_description="Статус доступности API")
async def healthcheck() -> HealthCheckResponse:
    """
    Проверка работоспособности API.
    """
    return HealthCheckResponse(status="ok")


@router.get("/mongo",
            summary="MongoDB",
            response_model=MongoHealthResponse,
            response_description="Статус MongoDB")
async def health_mongo(request: Request, service: HealthService = Depends(get_health_service)) -> JSONResponse:
    """
    Проверка доступности MongoDB.
    """
    try:
        result: dict[str, Any] = await service.mongo_health(request)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "mongo": "Error",
                "status": "MongoDB is unavailable",
                "error": str(e),
            }
        )


@router.get("/redis",
            summary="Redis",
            response_model=RedisHealthResponse,
            response_description="Статус Redis")
async def health_redis(service: HealthService = Depends(get_health_service)) -> JSONResponse:
    """
    Проверка доступности Redis.
    """
    try:
        result: dict[str, Any] = await service.redis_health()
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "redis": "Error",
                "status": "Redis is unavailable",
                "error": str(e),
            }
        )


@router.get("/postgre",
            summary="PostgreSQL",
            response_model=DBHealthResponse,
            response_description="Статус Postgre")
async def health_db(service: HealthService = Depends(get_health_service)) -> JSONResponse:
    """
    Проверка доступности базы данных PostgreSQL.
    """
    try:
        result: dict[str, Any] = await service.db_health()
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "db": "Error",
                "status": "Database error",
                "error": str(e),
            }
        )


@router.get("/summary",
            summary="Backend Server Info",
            response_model=HealthStatusResponse,
            response_description="Сводная информация о сервере (backend)")
async def summary_server_info(request: Request,
                              service: HealthService = Depends(
                                  get_health_service)) -> HealthStatusResponse | JSONResponse:
    """
    Получение сводной информации о состоянии сервера.
    """
    try:
        result: HealthStatusResponse = await service.system_status()
        return result
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(e)},
        )
