from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def profile_inline_kb():
    """
    Возвращает InlineKeyboardMarkup для профиля пользователя.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="📋 Карточки", callback_data="profile:cards")
    kb.button(text="  📊 Статистика  ", callback_data="profile:stats")
    kb.button(text="🔙 В меню", callback_data="profile:back")
    kb.adjust(2,)
    return kb.as_markup()


def profile_back_kb() -> InlineKeyboardMarkup:
    """Клавиатура с одной кнопкой 'Назад'."""
    keyboard = [
        [InlineKeyboardButton(text="🔙 Назад", callback_data="profile")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard, resize_keyboard=True)