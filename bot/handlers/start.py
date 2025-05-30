from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from bot.handlers.ui.ui_main import main_menu_inline_kb, build_access_request_keyboard
from core.infrastructure.database.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from core.infrastructure.database.user_ops import update_user_age

router = Router()


class Registration(StatesGroup):
    """Состояния для регистрации пользователя."""
    waiting_age = State()


def is_valid_age(age_text: str) -> bool:
    """
    Проверяет корректность введённого возраста.
    Возраст должен быть числом в диапазоне от 5 до 99.
    """
    return age_text.isdigit() and 5 <= int(age_text) <= 99


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """
    Обработка команды /start.
    Если пользователь уже одобрен и указал возраст — показывает главное меню.
    Если возраст не указан — запрашивает возраст.
    Если доступ не запрошен — предлагает запросить доступ.
    Если заявка на доступ уже отправлена — уведомляет об этом.
    """
    uid = message.from_user.id
    async with SQLAlchemyUserRepository() as repo:
        user = await repo.get_or_create(uid, message.from_user.full_name)

    # Если пользователь уже одобрен и возраст есть — показываем меню
    if user.is_approved and user.age is not None:
        await message.answer(
            f"Привет 👋, <b>{user.name}</b>! Выбирай раздел:",
            reply_markup=main_menu_inline_kb(user.is_admin)
        )

    if user.age is None:
        # Запрашиваем возраст, если ещё не введён
        await state.set_state(Registration.waiting_age)
        await message.answer(f"Привет, <b>{user.name or message.from_user.full_name}</b>! Сколько тебе лет?")
        return

    if not user.has_requested_access and not user.is_admin:
        await message.answer(
            "Спасибо! Теперь жми кнопку, чтобы запросить доступ.",
            reply_markup=build_access_request_keyboard()
        )
    elif not user.is_approved and not user.is_admin:
        await message.answer(
            "📩 Твой запрос на доступ уже отправлен.",
        )


@router.message(StateFilter(Registration.waiting_age), F.text)
async def process_age(message: Message, state: FSMContext):
    """
    Обработка ввода возраста пользователем.
    Проверяет корректность возраста и сохраняет его в базе данных.
    При некорректном вводе запрашивает возраст повторно.
    """
    data = await state.get_data()
    prompt_id = data.get("age_prompt_id")

    # Валидация
    if not is_valid_age(message.text):
        if prompt_id:
            await message.bot.delete_message(message.chat.id, prompt_id)
        sent = await message.answer(
            "Пожалуйста, введи корректный возраст цифрами (5–99)"
        )
        await state.update_data(age_prompt_id=sent.message_id)
        return

    await update_user_age(message.from_user.id, int(message.text))
    await state.clear()

    await cmd_start(message, state)
