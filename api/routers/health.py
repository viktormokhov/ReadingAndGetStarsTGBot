from fastapi import APIRouter, Request, status
from sqlalchemy import text
from starlette.responses import JSONResponse

from core.infrastructure.clients.redis_client import rc
from core.infrastructure.database.connection import sqlalchemy_engine

router = APIRouter(
    prefix="/api/v1/health",
    tags=["health"],
    # dependencies=[Depends(verify_api_key)],
    responses={404: {"description": "Not found"}},
)


@router.get("")
async def health_check():
    return {"status": "ok"}


@router.get("/mongo", summary="MongoDB health check")
async def health_mongo(request: Request):
    try:
        db = request.app.state.db
        await db.command("ping")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"mongo": "OK", "status": "MongoDB is healthy"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"mongo": "Error", "status": "MongoDB is unavailable"}
        )


@router.get("/health/redis", summary="Redis health check")
async def health_redis():
    try:
        pong = await rc.ping()
        if pong:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"redis": "OK", "status": "Redis is healthy"}
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"redis": "Error", "status": "Redis is not responding"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"redis": "Error", "status": "Redis is unavailable"}
        )


@router.get("/health/db", summary="Database health check")
async def health_db():
    try:
        async with sqlalchemy_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"db": "OK", "status": "Database is healthy"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"db": "Error", "status": f"Database error: {str(e)}"}
        )
