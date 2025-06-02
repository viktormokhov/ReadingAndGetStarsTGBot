from fastapi import APIRouter, Request, status, Depends
from starlette.responses import JSONResponse

from core.presentation.deps import verify_api_key
from core.application.services.health_service import (
    check_mongo_health,
    check_redis_health,
    check_db_health,
    get_summary_status
)
from core.presentation.health.schemas.response_health import (
    MongoHealthResponse,
    RedisHealthResponse,
    DBHealthResponse,
    HealthStatusResponse
)

router = APIRouter(
    prefix="/api/v1/health",
    tags=["health"],
    dependencies=[Depends(verify_api_key)],
    responses={404: {"description": "Not found"}},
)


@router.get("/mongo", summary="MongoDB health check", response_model=MongoHealthResponse)
async def health_mongo(request: Request):
    try:
        result = await check_mongo_health(request)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"mongo": "Error", "status": "MongoDB is unavailable", "error": str(e)}
        )


@router.get("/redis", summary="Redis health check", response_model=RedisHealthResponse)
async def health_redis():
    try:
        result = await check_redis_health()
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"redis": "Error", "status": "Redis is unavailable", "error": str(e)}
        )


@router.get("/postgre", summary="Database health check", response_model=DBHealthResponse)
async def health_db():
    try:
        result = await check_db_health()
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"db": "Error", "status": "Database error", "error": str(e)}
        )


@router.get("/summary", summary="Summary Server Info", response_model=HealthStatusResponse)
async def summary_server_info(request: Request):
    try:
        result = await get_summary_status()
        return result
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(e)},
        )
