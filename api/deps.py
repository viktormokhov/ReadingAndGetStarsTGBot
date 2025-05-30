from typing import Optional

from fastapi import Header, HTTPException
from starlette import status

from config.settings import backend_settings
from core.infrastructure.database.repository_factory import RepositoryFactory


async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != backend_settings.backend_api_key.get_secret_value():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )


async def user_repo_dep():
    return RepositoryFactory.create_user_repository()