from fastapi import APIRouter, Depends

from core.presentation.deps import verify_api_key

router = APIRouter(
    prefix="/api/v1/register-user",
    tags=["register-user"],
    dependencies=[Depends(verify_api_key)],
    responses={404: {"description": "Not found"}},
)