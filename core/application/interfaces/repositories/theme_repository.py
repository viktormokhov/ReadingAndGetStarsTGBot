from abc import ABC, abstractmethod


class ThemeRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    async def create(self, uid: int, name: str = None, is_admin: bool = False, is_approved: bool = False) -> User:
        pass