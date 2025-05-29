import logging
import random

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from core import config
from core.constants import MAX_ATTEMPTS
from handlers import ui
from core.database import themes
from core.database.text_log import log_text_generation
from core.database.user_ops import add_stars, update_streak
from core.models.reading_state import ReadingState
from core.services.clients.sqlalchemy import AsyncSessionLocal
from core.services.cards.process_card_generation import process_card_generation
from handlers.ui.ui_main import categories_kb

logger = logging.getLogger(__name__)


async def save_card_and_notify(call: CallbackQuery, state: FSMContext, qs: ReadingState, dispatcher):
    """
    Сохраняет результаты, начисляет звезды, уведомляет пользователя,
    сохраняет карточку при победе, очищает состояние.
    """
    async with AsyncSessionLocal() as session:
        await log_text_generation(session, qs.uid, qs.theme)
        bonus = await update_streak(qs.uid, session)
        stars = calculate_stars(qs)
        earned = stars + bonus
        await add_stars(qs.uid, earned, session)

    await themes.inc_theme(qs.uid, qs.theme)

    message = build_result_message(qs, earned, bonus)
    await call.message.edit_text(message)

    if qs.wrong < MAX_ATTEMPTS:
        if not await process_card_generation(call, qs, logger, dispatcher=dispatcher):
            await call.message.answer("📂 Выбери раздел:", reply_markup=categories_kb())
            await state.clear()
            return

    await call.message.answer("📂 Выбери раздел:", reply_markup=categories_kb())
    await state.clear()


def calculate_stars(qs: ReadingState) -> int:
    """Подсчитывает количество звезд за викторину."""
    base_stars = count_stars(qs.full_text)
    # Учёт ошибок: штраф = (1 - qs.wrong / total_questions)
    total = len(qs.qa)
    mistakes = qs.wrong

    # Если ошибок столько же, сколько вопросов, ставим 0 звёзд
    if mistakes == total:
        return 0
    return max(1, int(base_stars * (1 - 0.5 * (mistakes / total))))


def count_stars(text: str) -> int:
    """Считает количество звёзд: 1 за каждые 10 слов (минимум 1)."""
    return max(1, int(len(text.split()) * 0.1))


def build_result_message(qs: ReadingState, earned: int, bonus: int) -> str:
    """Формирует текст сообщения о результате викторины."""
    total = len(qs.qa)
    mistakes = qs.wrong
    words = len(qs.full_text.split())
    if mistakes == 0:
        msg = random.choice([
            "Отлично", "Молодец", "Ты крутой, продолжай в том же духе"
        ]) + f"!\nБез ошибок! Ты заработал <b>{earned}</b> ⭐\n📖 Прочитано слов: <b>{words}</b>"
    else:
        msg = (f"Викторина завершена!\nОшибок: {mistakes}/{total}\n"
               f"Ты заработал <b>{earned}</b> ⭐\n📖 Прочитано слов: <b>{words}</b>")
    if bonus:
        msg += f" (+{bonus} ⭐ за серию)"
    return msg
