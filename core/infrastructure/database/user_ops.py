from datetime import date, timedelta
from datetime import datetime, UTC
from typing import Optional

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.infrastructure.database.connection import AsyncSessionLocal
from core.infrastructure.database.models import User, ThemeStat, UserCards, UserStars, UserQuizzes



class UserService:
    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session
        self._external_session = session is not None

    async def __aenter__(self):
        if not self._session:
            self._session = AsyncSessionLocal()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if not self._external_session and self._session:
            await self._session.close()

    @property
    def session(self) -> AsyncSession:
        if not self._session:
            raise RuntimeError("Session is not initialized")
        return self._session















# --- Работа с пользователями ---
# async def get_or_create_user(user_id: int, name: str | None = None) -> User:
#     async with AsyncSessionLocal() as session:
#         user = await session.get(User, user_id)
#         if not user:
#             user = await create_user(user_id, name, session)
#         return user


# async def get_user(uid: int) -> type[User]:
#     """Получает пользователя из базы данных по его ID."""
#     async with AsyncSessionLocal() as session:
#         user = await session.get(User, uid)
#         if user is None:
#             raise ValueError(f"User with id {uid} not found")
#         return user


# async def create_user(uid: int, name: str, session: AsyncSession) -> User:
#     """
#     Создаёт нового пользователя с указанным ID.
#
#     Args:
#         uid (int): Идентификатор пользователя.
#         name (str): Имя пользователя.
#         session (AsyncSession): Асинхронная сессия SQLAlchemy.
#
#     Returns:
#         User: Созданный пользователь.
#     """
#     user = User(id=uid, is_approved=False, name=name)
#     session.add(user)
#     await session.commit()
#     return user


async def update_user_age(user_id: int, age: int):
    async with AsyncSessionLocal.begin() as session:
        user = await session.get(User, user_id)
        user.age = age
        await session.commit()


async def get_all_user_ids(session: AsyncSession) -> list[int]:
    """
    Возвращает список всех ID пользователей.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Returns:
        List[int]: Список идентификаторов пользователей.
    """
    result = await session.execute(select(User.id))
    return [row[0] for row in result.all()]


async def get_user_age(uid: int, session: AsyncSession) -> Optional[int]:
    """
    Получает возраст пользователя.

    Args:
        uid (int): Идентификатор пользователя.
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Returns:
        Optional[int]: Возраст пользователя или None, если пользователь не найден.
    """
    user = await session.get(User, uid)
    return user.age if user else None


# def select_users_where(predicate: Callable[[User], object]) -> select:
#     """
#     Формирует SQL-выражение для выборки пользователей по предикату.
#
#     Args:
#         predicate (Callable): Функция, возвращающая условие для where.
#
#     Returns:
#         select: SQL-выражение select.
#     """
#     return select(User).where(predicate(User))


# --- Работа со статистикой по темам ---
def select_user_theme_stats(user_id: int) -> select:
    """
    Формирует SQL-выражение для выборки ThemeStat пользователя.

    Args:
        user_id (int): Идентификатор пользователя.

    Returns:
        select: SQL-выражение select.
    """
    return select(ThemeStat).where(ThemeStat.user_id == user_id)


def delete_theme_stats_for_user(user_id: int) -> delete:
    """
    Формирует SQL-выражение для удаления ThemeStat пользователя.

    Args:
        user_id (int): Идентификатор пользователя.

    Returns:
        delete: SQL-выражение delete.
    """
    return delete(ThemeStat).where(ThemeStat.user_id == user_id)


async def update_user_accuracy(uid: int, correct: bool, session: AsyncSession):
    """
    Обновляет статистику точности пользователя.

    Args:
    uid (int): Идентификатор пользователя.
    correct (bool): Был ли ответ верным.
    session (AsyncSession): Асинхронная сессия SQLAlchemy.
    """
    user = await get_or_create_user(uid)
    user.q_tot = (user.q_tot or 0) + 1
    user.q_ok = (user.q_ok or 0) + int(correct)
    await session.commit()


async def get_total_questions(user_id: int, session: AsyncSession) -> int:
    """
    Получает общее количество вопросов пользователя (ThemeStat.texts).

    Args:
        user_id (int): Идентификатор пользователя.
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Returns:
        int: Суммарное количество вопросов или 0, если нет записей.
    """
    result = await session.execute(
        select(func.sum(ThemeStat.texts)).where(ThemeStat.user_id == user_id)
    )
    return result.scalar() or 0


# --- Работа с карточками и звездами---
def select_user_card_counts(user_id: int) -> select:
    """
    Формирует SQL-выражение для подсчёта количества карточек пользователя.

    Args:
        user_id (int): Идентификатор пользователя.

    Returns:
        select: SQL-выражение select.
    """
    return select(func.count()).select_from(UserCards).where(UserCards.user_id == user_id)


async def get_user_card_count(user_id: int, session: AsyncSession) -> int:
    """
    Получает количество карточек у пользователя.

    Args:
        user_id (int): Идентификатор пользователя.
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Returns:
        int: Количество карточек или 0, если нет записей.
    """
    result = await session.execute(
        select(func.count()).select_from(UserCards).where(UserCards.user_id == user_id)
    )
    return result.scalar() or 0


async def add_user_stars(uid: int, count: int, session: AsyncSession) -> UserStars:
    """Добавляет звёзды пользователю."""
    stmt = select(UserStars).where(UserStars.user_id == uid)
    result = await session.execute(stmt)
    user_stars = result.scalar_one_or_none()

    if user_stars:
        user_stars.count += count
        user_stars.updated_at = datetime.now(UTC)
    else:
        user_stars = UserStars(user_id=uid, count=count)
        session.add(user_stars)

    return user_stars


async def add_user_quiz(user_id: int, quiz_data: dict, session: AsyncSession = None) -> UserQuizzes:
    """Добавляет результат квиза для пользователя."""
    if session is None:
        async with AsyncSessionLocal.begin() as session:
            return await add_user_quiz(user_id, quiz_data, session)

    quiz = UserQuizzes(user_id=user_id, **quiz_data)
    session.add(quiz)

    await session.flush()
    await session.commit()
    return quiz


async def update_streak(uid: int, session: AsyncSession) -> int:
    """
    Обновляет серию активности пользователя.
    Возвращает 5 за продолжение серии, иначе 0.

    Args:
        uid (int): Идентификатор пользователя.
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Returns:
        int: Бонус за продолжение streak (5 или 0).
    """
    user = await get_or_create_user(uid)
    today = date.today()
    # Если streak уже сегодня обновлялся — возвращаем 0
    if user.last == today:
        return 0

    # Бонус если предыдущий last — ровно вчера
    bonus = 5 if user.last and (today - user.last == timedelta(days=1)) else 0
    user.streak = (user.streak or 0) + 1 if bonus else 1
    user.last = today

    await session.commit()
    return bonus
