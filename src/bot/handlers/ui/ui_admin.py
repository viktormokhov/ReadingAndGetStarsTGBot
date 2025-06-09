from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_panel_inline_kb():
    """
    Возвращает InlineKeyboardMarkup для панели администратора.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="📋 Заявки на доступ", callback_data="admin:requests")
    kb.button(text="  📊 Все пользователи  ", callback_data="admin:all_users:0")
    kb.button(text="ℹ️ Пользователь", callback_data="admin:lookup_user")
    kb.button(text="📈 Статистика", callback_data="admin:stats")
    kb.button(text="🔄 Перезагрузить бота", callback_data="admin:restart")
    kb.button(text="🔑 Сбросить ключи Redis", callback_data="admin:redis_del")
    # Кнопка "Назад" последней
    kb.button(text="🔙 В меню", callback_data="admin:back")
    kb.adjust(2, 2, 1, 1)  # 2 в ряд, потом 1 отдельная кнопка
    return kb.as_markup()

def admin_back_menu_kb():
    """
    Возвращает инлайн-клавиатуру с одной кнопкой "В меню" для возврата в админ-панель.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin")]
        ]
    )

def admin_pagination_kb(page: int, total: int, page_size: int):
    """
    Возвращает инлайн-клавиатуру для пагинации с кнопкой "В меню".
    :param page: текущая страница
    :param total: общее количество элементов
    :param page_size: количество на странице
    """
    kb = InlineKeyboardBuilder()
    if page > 0:
        kb.button(text="◀️ Назад", callback_data=f"admin:all_users:{page - 1}")
    if (page + 1) * page_size < total:
        kb.button(text="▶️ Вперёд", callback_data=f"admin:all_users:{page + 1}")
    kb.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="admin")
    )
    return kb.as_markup()

def admin_user_manage_kb(user_id: int):
    """
    Возвращает инлайн-клавиатуру для управления пользователем:
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="♻️ Сброс", callback_data=f"reset_user:{user_id}")
    kb.button(text="🗑 Удалить", callback_data=f"delete_user:{user_id}")
    kb.button(text="🔙 Назад", callback_data="admin:lookup_user")
    kb.adjust(2)
    return kb.as_markup()