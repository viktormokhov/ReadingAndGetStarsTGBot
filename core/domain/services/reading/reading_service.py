import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.handlers.ui.ui_main import reading
from config.constants import DAILY_LIMIT_PER_THEME
from core.domain.models.state import ReadingState
from core.domain.services.ai.llm_text_content_generator import LLMTextContentGenerator
from core.infrastructure.database.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository


async def has_exceeded_daily_limit(uid: int, theme: str) -> bool:
    """Проверяет, превышен ли дневной лимит генерации по теме для пользователя."""
    async with SQLAlchemyUserRepository() as repo:
        count = await repo.get_generated_count_today_by_user(uid, theme)
        return count >= DAILY_LIMIT_PER_THEME


async def prepare_first_question(uid: int, category: str, theme: str) -> ReadingState:
    """Создаёт и возвращает начальное состояние викторины по теме для пользователя."""
    async with SQLAlchemyUserRepository() as repo:
        get_age = await repo.get_by_id(uid)
        age = get_age.age

    generator = LLMTextContentGenerator(
        uid=uid,
        theme=theme,
        age=age
    )
    e = await generator.generate_text(category)
    first = e["qa"][0]

    return ReadingState(
        uid=uid,
        theme=theme,
        qa=e["qa"],
        asked={first["question"]},
        correct=first["options"][0],
        wrong=0,
        card_title=e["card"],
        word_count=len(e["text"].split()),
        full_text=e["text"]
    )


async def prepare_next_question(call: CallbackQuery, state: FSMContext, qs: ReadingState):
    """Готовит и задаёт следующий вопрос пользователю в викторине."""
    # Удаляем предыдущее сообщение с вопросом и фидбек, если есть
    try:
        await call.bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    except Exception:
        pass

    # Удаляем предыдущее мотивационное сообщение (если есть)
    prev_fb_id = (await state.get_data()).get("feedback_msg_id")
    if prev_fb_id:
        try:
            await call.bot.delete_message(chat_id=call.message.chat.id, message_id=prev_fb_id)
        except Exception:
            pass

    # Находим следующий не заданный вопрос, иначе — докидываем новые
    next_q = next((qa for qa in qs.qa if qa["question"] not in qs.asked), None)
    # if not next_q:
    #     # Если вдруг вопросы закончились — добавим ещё (или обработаем как надо)
    #     extra = await entry(qs.uid, qs.theme)
    #     qs.qa.extend(extra["qa"])
    #     next_q = extra["qa"][0]

    qs.correct = next_q["options"][0]
    qs.asked.add(next_q["question"])

    # Новое мотивационное сообщение
    sent_fb = await call.message.answer("💪 Не сдавайся!", protect_content=True)
    qs.feedback_msg_id = sent_fb.message_id

    # Сохраняем state и варианты для проверки ответа
    await state.update_data(**qs.__dict__)
    keyboard, options = reading(next_q["options"])
    await state.update_data(reading_options=options)

    # Пауза
    await asyncio.sleep(1)

    # Новый вопрос
    await call.message.answer(
        f"<b>{next_q['question']}</b>",
        protect_content=True,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
