import random
from typing import List

from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.config.settings import WEBAPP_URL
from src.config.content import CATEGORIES, build_display


# === Базовые утилиты ===
def button(text: str, data: str) -> InlineKeyboardButton:
    """Упрощённый конструктор кнопки."""
    return InlineKeyboardButton(text=text, callback_data=data)


def build_menu(buttons, n_cols=2):
    """Разбивает список кнопок на ряды по n_cols в каждом."""
    return [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]


def inline(rows: List[List[InlineKeyboardButton]]) -> InlineKeyboardMarkup:
    """Формирует InlineKeyboardMarkup из строк кнопок."""
    return InlineKeyboardMarkup(inline_keyboard=rows)


# === Клавиатуры викторины ===

def reading(opts: list[str]) -> InlineKeyboardMarkup:
    """Возвращает клавиатуру викторины с перемешанными вариантами и короткими callback_data."""
    opts = opts[:]  # создаём копию, чтобы не перемешивать оригинальный список
    random.shuffle(opts)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=opt, callback_data=f'OPT|{i}')]
            for i, opt in enumerate(opts)
        ]
    ), opts


# === Категории и темы ===
def categories_kb() -> InlineKeyboardMarkup:
    # """Меню категорий."""
    buttons = [
        InlineKeyboardButton(text=cat, callback_data=f"cat|{cat}")
        for cat in CATEGORIES
    ]
    # Группировка по 2 кнопки в ряд
    keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    keyboard.append([InlineKeyboardButton(text="🔙 В меню", callback_data="reading:back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard, resize_keyboard=True)


def topics_kb(category: str) -> InlineKeyboardMarkup:
    """Меню тем внутри категории."""
    display = build_display()
    buttons = [button(display[t], f"T|{t}") for t, _ in CATEGORIES[category]]
    rows = build_menu(buttons, n_cols=2)  # по 2 кнопки в ряду
    rows.append([button("⬅️ Назад", "back_to_categories")])
    return inline(rows)


def build_access_request_keyboard():
    kb = InlineKeyboardBuilder()
    # Всегда кнопка "Запросить доступ"
    kb.button(text="🔓 Запросить доступ", callback_data="request_access")
    return kb.as_markup()


def back_kb() -> InlineKeyboardMarkup:
    """Клавиатура с одной кнопкой 'Назад'."""
    keyboard = [
        [InlineKeyboardButton(text="🔙 В меню", callback_data="reading:back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard, resize_keyboard=True)


def main_menu_inline_kb(is_admin: bool = False):
    kb = InlineKeyboardBuilder()
    # kb.button(text="📚 Чтение", callback_data="reading")
    kb.button(text="📋 Читайка", web_app=WebAppInfo(url=WEBAPP_URL))
    # kb.button(text="👤 Профиль", callback_data="profile")
    # kb.button(text="🃏 Карточки", callback_data="cards")
    # kb.button(text="  📊 Статистика  ", callback_data="stats")
    # kb.button(text="💸 Баланс", callback_data="withdrawal")
    # kb.button(text="⚙️ Настройки", callback_data="settings")

    if is_admin:
        kb.button(text="🛠️ Admin Panel", callback_data="admin")
    kb.adjust(1)
    return kb.as_markup(row_width=1)

def get_start_keyboard(is_admin: bool = False) -> types.InlineKeyboardMarkup:
    keyboard = []

    # Кнопка WebApp
    webapp_button = types.InlineKeyboardButton(
        text="Читайка",
        web_app=types.WebAppInfo(url=WEBAPP_URL)
    )
    keyboard.append([webapp_button])

    if is_admin:
        admin_button = types.InlineKeyboardButton(
            text="🛠️ Admin Panel",
            callback_data="admin"
        )
        keyboard.append([admin_button])

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)
