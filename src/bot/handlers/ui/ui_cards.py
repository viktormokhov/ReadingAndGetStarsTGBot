from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config.constants import CARDS_PER_PAGE, CARDS_ROW_WIDTH


def card_filter_kb(themes: list[str]) -> InlineKeyboardMarkup:
    """
    Формирует inline-клавиатуру для списка тем карточек.
    """
    builder = InlineKeyboardBuilder()
    for th in themes:
        builder.button(text=th, callback_data=f"CARD_THEME|{th}")
    # возвращаем клавиатуру с 4 кнопками в ряду
    return builder.as_markup(row_width=4)

def card_filter_paged_kb(themes: list[str], page: int) -> InlineKeyboardMarkup:
    total_pages = (len(themes) + CARDS_PER_PAGE - 1) // CARDS_PER_PAGE
    page = max(1, min(page, total_pages))

    start = (page - 1) * CARDS_PER_PAGE
    end = start + CARDS_PER_PAGE
    page_themes = themes[start:end]

    # Строго делим по два
    rows = [page_themes[i:i + CARDS_ROW_WIDTH] for i in range(0, len(page_themes), CARDS_ROW_WIDTH)]

    keyboard = []
    for row in rows:
        buttons = [
            InlineKeyboardButton(text=th, callback_data=f"CARD_THEME|{th}")
            for th in row
        ]
        keyboard.append(buttons)

    # Навигация
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"CARD_PAGE|{page - 1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"CARD_PAGE|{page + 1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)

    # Кнопка закрыть
    keyboard.append([InlineKeyboardButton(text="❌ Закрыть", callback_data="CLOSE_CARDS")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def cards_pagination_kb(page: int, total_pages: int) -> InlineKeyboardMarkup:
    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"CARD_PAGE_PHOTO|{page - 1}"))
    if page < total_pages:
        buttons.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"CARD_PAGE_PHOTO|{page + 1}"))
    if buttons:
        return InlineKeyboardMarkup(
            inline_keyboard=[buttons, [InlineKeyboardButton(text="❌ Закрыть", callback_data="CLOSE_CARDS")]])
    else:
        return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="❌ Закрыть", callback_data="CLOSE_CARDS")]])


