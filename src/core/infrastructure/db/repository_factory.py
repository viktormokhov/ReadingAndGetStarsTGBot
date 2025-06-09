from core.application.interfaces.repositories.user_repository import UserRepositoryInterface
# from core.application.interfaces.repositories.card_repository import CardRepositoryInterface

from core.infrastructure.db.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
# from core.infrastructure.db.repositories.sqlalchemy_card_repository import SQLAlchemyCardRepository


class RepositoryFactory:
    @staticmethod
    def create_user_repository() -> UserRepositoryInterface:
        return SQLAlchemyUserRepository()

    # @staticmethod
    # def create_card_repository() -> CardRepositoryInterface:
    #     return SQLAlchemyCardRepository()