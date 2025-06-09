from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Depends, Header, Body, Request
from starlette.responses import JSONResponse

from config.settings import get_openai_settings, get_minio_settings
from core.application.services.avatar_service import AvatarService
from core.domain.models.user import UserProfileResponse
from core.infrastructure.ai.openai_image_generator import OpenAIImageGenerator
from core.infrastructure.database.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from core.infrastructure.image_tools import ImageTools
from core.infrastructure.storage.minio_storage import MinioImageStorage
from core.presentation.deps import verify_api_key
from core.presentation.user.schemas.user_schema import GenerateAvatarResponse, GenerateAvatarRequest

router = APIRouter(
    prefix="/api/v1/users",
    tags=["user"],
    # dependencies=[Depends(verify_api_key)],
    responses={404: {"description": "Not found"}},
)

def get_avatar_service(request: Request) -> AvatarService:
    minio_client = request.app.state.minio_client
    redis_client = request.app.state.redis

    ai_settings = get_openai_settings()
    minio_settings = get_minio_settings()

    image_generator = OpenAIImageGenerator(ai_settings.api_key)
    image_storage = MinioImageStorage(
        minio_client,
        "avatars",
        f"https://{minio_settings.endpoint_url}"
    )
    image_tools = ImageTools(redis_client)  # <-- передаёшь redis-клиент
    return AvatarService(image_generator, image_storage, image_tools)


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(user_id: int = Query(..., alias="userId")):
    try:
        async with SQLAlchemyUserRepository() as repo:
            user_data = await repo.get_by_id(user_id)

        if not user_data:
            return JSONResponse(
                status_code=200,
                content={"success": False, "error": "User not found", "data": None}
            )

        return UserProfileResponse(success=True, data=user_data.model_dump())

    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка получения профиля пользователя: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e), "data": None}
        )


@router.post("/generate-avatar",
             response_model=GenerateAvatarResponse)
async def generate_avatar(
        req: GenerateAvatarRequest,
        avatar_service: AvatarService = Depends(get_avatar_service)
):
    try:
        avatar_url, avatar_uuid = await avatar_service.generate_avatar_and_cache(req.prompt, req.user_id)
        if avatar_url is None:
            return JSONResponse(
                status_code=200,
                content={"success": False, "error": "The image was not generated"}
            )
        return {"success": True, "avatar_url": avatar_url, "avatar_uuid": avatar_uuid}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@router.get("/{user_id}/avatar-attempts")
async def get_avatar_attempts(
        user_id: int,
        avatar_service: AvatarService = Depends(get_avatar_service)
):
    try:
        attempts = await avatar_service.get_avatar_attempts(user_id)
        return {"attempts": attempts}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )


@router.post("/{user_id}/avatar-attempts")
async def increment_avatar_attempts(
        user_id: int,
        avatar_service: AvatarService = Depends(get_avatar_service)
):
    try:
        attempts, key = await avatar_service.increment_avatar_attempts(user_id)
        return {"attempts": attempts, "attempt_key": key}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )
