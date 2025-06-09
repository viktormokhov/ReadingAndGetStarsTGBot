from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy import select

from src.core.domain.models.user import User


class UserRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    async def create(self, uid: int, name: str = None, is_admin: bool = False, is_approved: bool = False) -> User:
        pass

    @abstractmethod
    async def get_or_create(self, user_id: int, name: str = None) -> User:
        pass

    @abstractmethod
    async def save_user(self, user: User):
        pass

    @abstractmethod
    async def update_user_status(self, user_id: int, status: str):
        pass

    @abstractmethod
    async def get_all(self) -> Optional[list[User]]:
        pass

    @abstractmethod
    async def get_not_approved(self) -> Optional[list[User]]:
        pass

    @abstractmethod
    async def select_where(self) -> select:
        pass

    @abstractmethod
    async def get_theme_by_user(self, user_id: int):
        pass

    @abstractmethod
    async def get_questions_count_by_user(self, user_id: int) -> int:
        pass

    @abstractmethod
    async def get_card_count_by_user(self, user_id: int) -> int:
        pass

    @abstractmethod
    async def get_stars_count_by_user(self, user_id: int) -> int:
        pass

    @abstractmethod
    async def get_generated_count_today_by_user(self, user_id: int, theme: str) -> int:
        pass






