import logging

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import Card

logger = logging.getLogger(__name__)


async def save_card(uid: int, theme: str, title: str, url: str, session: AsyncSession) -> Card:
    """
    Добавляет новую карточку в базу данных.

    Args:
        uid (int): ID пользователя.
        theme (str): Тема карточки.
        title (str): Заголовок карточки.
        url (str): URL карточки.
        session (AsyncSession): Сессия SQLAlchemy.

    Returns:
        Card: Добавленная карточка.
    """
    card = Card(
        user_id=uid,
        theme=theme,
        title=title,
        url=url
    )
    session.add(card)
    await session.commit()
    return card


async def is_card_duplicate(uid: int, theme: str, title: str, session: AsyncSession) -> bool:
    """
    Проверяет, существует ли карточка с заданным пользователем, темой и заголовком.

    Args:
        uid (int): ID пользователя.
        theme (str): Название темы.
        title (str): Заголовок карточки.
        session (AsyncSession): Сессия SQLAlchemy.

    Returns:
        bool: True, если дубликат найден, иначе False.
    """
    exists = await session.scalar(
        select(func.count())
        .select_from(Card)
        .where(
            Card.user_id == uid,
            Card.theme == theme,
            Card.title == title
        )
    )
    return bool(exists)
