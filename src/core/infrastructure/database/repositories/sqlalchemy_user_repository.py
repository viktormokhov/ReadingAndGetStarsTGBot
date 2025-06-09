from datetime import date
from typing import Optional, List, Callable

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.application.interfaces.repositories.user_repository import UserRepositoryInterface
from src.core.domain.models.user import User
from src.core.infrastructure.database.connection import AsyncSessionLocal
from src.core.infrastructure.database.models import User as UserORM, ThemeStat, UserCards, UserStars, TextGeneration


class SQLAlchemyUserRepository(UserRepositoryInterface):
    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session
        self._external_session = session is not None

    async def __aenter__(self):
        if not self._session:
            self._session = AsyncSessionLocal()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if not self._external_session:
            if exc_type:
                await self._session.rollback()
            else:
                await self._session.commit()
            await self._session.close()

    @property
    def session(self) -> AsyncSession:
        if not self._session:
            raise RuntimeError("Session is not initialized")
        return self._session

    async def get_by_id(self, telegram_id: int) -> Optional[User]:
        q = select(UserORM).where(UserORM.telegram_id == telegram_id)
        res = await self.session.execute(q)
        user = res.scalar_one_or_none()
        if user is None:
            return None
        return self._map_to_domain(user)

    async def create(self, uid: int, name: str = None, is_admin: bool = False, status: str = 'pending') -> User:
        """Создаёт нового пользователя с указанным Telegram ID."""
        user = UserORM(telegram_id=uid, name=name, is_admin=is_admin, status=status)
        self.session.add(user)
        await self.session.flush()
        return self._map_to_domain(user)

    async def get_or_create(self, uid: int, name: str | None = None) -> Optional[User]:
        user = await self.session.get(UserORM, uid)
        if not user:
            user = await self.create(uid, name)
        return self._map_to_domain(user)

    async def save_user(self, user: User):
        pass

    async def update_user_status(self, user_id: int, status: str):
        pass

    async def get_all(self) -> Optional[list[User]]:
        result = await self.session.execute(select(UserORM))
        users = result.scalars().all()
        return [self._map_to_domain(user) for user in users]

    async def get_not_approved(self) -> List[User]:
        result = await self.session.execute(
            select(UserORM).where(UserORM.is_approved == False)
        )
        users = result.scalars().all()
        return [self._map_to_domain(user) for user in users]

    async def select_where(self, predicate: Callable[[UserORM], object]) -> select:
        return select(UserORM).where(predicate(UserORM))

    async def get_theme_by_user(self, user_id: int):
        stmt = select(ThemeStat).where(ThemeStat.user_id == user_id)
        result = await self.session.scalars(stmt)
        return result.all()

    async def get_questions_count_by_user(self, user_id: int) -> int:
        stmt = select(func.sum(ThemeStat.texts)).where(ThemeStat.user_id == user_id)
        result = await self.session.execute(stmt)
        questions_count = result.scalar() or 0
        return questions_count

    async def get_card_count_by_user(self, user_id: int) -> int:
        stmt = select(func.count()).select_from(UserCards).where(UserCards.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_stars_count_by_user(self, uid: int) -> int:
        stmt = select(func.sum(UserStars.count)).where(UserStars.user_id == uid)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_generated_count_today_by_user(self, user_id: int, theme: str) -> int:
        today = date.today()
        stmt = select(func.count()).select_from(TextGeneration).where(
            TextGeneration.user_id == user_id,
            TextGeneration.theme == theme,
            func.date(TextGeneration.created_at) == today
        )
        result = await self.session.execute(stmt)
        return result.scalar()

    def _map_to_domain(self, user_orm: UserORM) -> User:
        # Преобразование ORM-модели в доменную модель
        return User(
            id=user_orm.id,
            name=user_orm.name,
            age=user_orm.age,
            is_admin=user_orm.is_admin,
            status=user_orm.status,
            # has_requested_access=user_orm.has_requested_access,
            # q_ok=user_orm.q_ok,
            # q_tot=user_orm.q_tot,
            # streak=user_orm.streak,
            # last=user_orm.last,
            telegram_id=user_orm.telegram_id,
            first_active=user_orm.first_active,
            last_active=user_orm.last_active
        )
