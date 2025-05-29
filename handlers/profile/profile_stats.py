from typing import Union

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from core.decorators.approved_user_only import is_approved_user
from core.services.users.formatter import format_stats
from core.services.users.user_progress import user_summary
from handlers.ui.ui_profile import profile_back_kb

router = Router()


@router.callback_query(F.data == "profile:stats")
@is_approved_user()
async def stats_command(message: Message):
    """Обработчик callback-запроса для отображения статистики пользователя."""
    await render_stats(message.from_user.id, message)


async def render_stats(user_id: int, target: Union[Message, CallbackQuery]):
    """Формирует и отправляет статистику пользователю."""
    summary = await user_summary(user_id)

    if not summary:
        msg = "Нет данных."
        send = target.message.answer if isinstance(target, CallbackQuery) else target.reply
        await send(msg)
        return

    text = format_stats(summary)
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text, reply_markup=profile_back_kb())
    else:
        await target.reply(text, reply_markup=profile_back_kb())
