from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException

from config.settings import get_tg_settings
from core.domain.models.user import RegistrationRequest
from core.domain.services.telegram.telegram_validation_service import validate_telegram_webapp_data
from core.domain.services.users.user_service import calculate_age
from core.presentation.deps import verify_api_key

router = APIRouter(
    prefix="/api/v1/user",
    tags=["user"],
    dependencies=[Depends(verify_api_key)],
    responses={404: {"description": "Not found"}},
)

@router.post("/create_account", response_model=dict)
async def register_user(
        request: RegistrationRequest,
        background_tasks: BackgroundTasks
):
    """Регистрация нового пользователя"""
    tg_settings = get_tg_settings()
    try:
        # Валидация данных Telegram
        bot_token = tg_settings.tg_bot_token
        if request.init_data and bot_token:
            is_valid = validate_telegram_webapp_data(request.init_data, bot_token)
            if not is_valid:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid Telegram authentication"
                )
            print(f"✅ Telegram данные валидны для пользователя: {request.telegram_id}")

        # Вычисляем возраст
        age = calculate_age(request.birth_date)

        # Создаем данные пользователя
        user_data = {
            "telegram_id": request.telegram_id,
            "name": request.name,
            "age": age,
            "birth_date": request.birth_date,
            "avatar": request.avatar,
            "stars": 0,
            "total_questions": 0,
            "card_count": 0,
            "is_admin": False,
            "status": "pending",
            "registered_at": datetime.now().isoformat()
        }

        # Здесь должно быть сохранение в базу данных
        # Для примера создаем mock ответ
        user_response = UserResponse(
            id=request.telegram_id,  # В реальности это будет ID из БД
            name=request.name,
            age=age,
            telegram_id=request.telegram_id,
            avatar=request.avatar,
            status="pending"
        )

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