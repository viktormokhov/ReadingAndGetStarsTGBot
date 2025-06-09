from src.core.application.interfaces.repositories.user_repository import UserRepositoryInterface
# from core.application.interfaces.repositories.card_repository import CardRepositoryInterface

from src.core.infrastructure.database.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
# from core.infrastructure.database.repositories.sqlalchemy_card_repository import SQLAlchemyCardRepository


class RepositoryFactory:
    @staticmethod
    def create_user_repository() -> UserRepositoryInterface:
        return SQLAlchemyUserRepository()

    # @staticmethod
    # def create_card_repository() -> CardRepositoryInterface:
    #     return SQLAlchemyCardRepository()