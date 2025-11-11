from db.postgres_models import UsersORM
from enums import USER_TYPE
from models import User
from mappers.abc_mapper import ABCMapper


class UserMapper(ABCMapper):
    @staticmethod
    def to_dto(entity: UsersORM) -> User:
        """
        Преобразует UsersORM в User (DTO)
        """
        return User(
            telegram_id=entity.telegram_id,
            full_name=entity.full_name,
            user_type=entity.user_type
        )

    @staticmethod
    def to_entity(dto: User) -> UsersORM:
        """
        Преобразует User (DTO) в UsersORM
        """
        return UsersORM(
            telegram_id=dto.telegram_id,
            full_name=dto.full_name,
            user_type=dto.user_type
        )

