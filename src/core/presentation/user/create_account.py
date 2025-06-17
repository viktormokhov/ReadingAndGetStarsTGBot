import logging
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, HTTPException
from sqlalchemy import select

from config.settings import get_tg_settings
from core.domain.models.user import UserResponse
from core.infrastructure.db.models import User as UserORM
from core.infrastructure.db.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from core.infrastructure.telegram.telegram_validation_service import validate_telegram_webapp_data
from core.presentation.user.schemas.user_schema import RegistrationRequest
from core.utils.telegram_utils import notify_admin_about_registration

router = APIRouter(
    prefix="/api/v1/user",
    tags=["user"],
    # dependencies=[Depends(verify_api_key)],
    responses={404: {"description": "Not found"}},
)

@router.post("/create-account", response_model=dict)
async def register_user(
        request: RegistrationRequest,
        background_tasks: BackgroundTasks
):
    """Регистрация нового пользователя"""
    tg_settings = get_tg_settings()
    try:
        # Валидация данных Telegram
        bot_token = tg_settings.bot_token
        if request.init_data and bot_token:
            is_valid = validate_telegram_webapp_data(request.init_data, bot_token)
            if not is_valid:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid Telegram authentication"
                )
            logging.info(f"✅ Telegram данные валидны для пользователя: {request.telegram_id}")

        # Преобразуем дату рождения из строки в объект date
        birth_date = datetime.strptime(request.birth_date, '%Y-%m-%d').date()

        # Сохраняем пользователя в базу данных
        try:
            async with SQLAlchemyUserRepository() as repo:
                # Проверяем, существует ли уже пользователь с таким telegram_id
                existing_user = await repo.get_by_id(request.telegram_id)
                if existing_user:
                    raise HTTPException(
                        status_code=400,
                        detail=f"User with telegram_id {request.telegram_id} already exists"
                    )

                # Создаем нового пользователя
                user = await repo.create(
                    uid=request.telegram_id,
                    name=request.name,
                    gender=request.gender,
                    birth_date=birth_date,
                    is_admin=False,
                    status="pending"
                )

                # Обновляем аватар пользователя
                q = select(UserORM).where(UserORM.telegram_id == request.telegram_id)
                result = await repo.session.execute(q)
                user_orm = result.scalar_one_or_none()
                if user_orm:
                    user_orm.avatar = request.avatar
                    await repo.session.commit()

                # Создаем объект ответа
                user_response = UserResponse(
                    name=user.name,
                    gender=user.gender,
                    telegram_id=user.telegram_id,
                    avatar=request.avatar,
                    status=user.status,
                    registered_at=user.registered_at,
                    birth_date=user.birth_date,
                    stars=0,
                    total_questions=0,
                    card_count=0,
                    is_admin=user.is_admin
                )
        except Exception as e:
            logging.error(f"Ошибка при сохранении пользователя в базу данных: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

        # Отправляем уведомление администратору в фоне
        background_tasks.add_task(
            notify_admin_about_registration,
            user_response,
            request.birth_date
        )

        print(f"Пользователь зарегистрирован и ожидает модерации: {user_response}")

        return {
            "success": True,
            "data": user_response.dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка регистрации пользователя: {e}")
        raise HTTPException(status_code=500, detail=str(e))
