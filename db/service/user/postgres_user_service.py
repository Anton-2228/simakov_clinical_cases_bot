from typing import List, Optional

from sqlalchemy import select

from db.postgres import SESSION_FACTORY
from db.postgres_models import UsersORM
from db.service.user.async_user_service import AsyncUserService
from enums import USER_TYPE
from models import User
from mappers.user_mapper import UserMapper


class PostgresUserService(AsyncUserService):
    async def save_user(self, user: User) -> str:
        """
        Метод асинхронно сохраняет пользователя в базу данных

        :return:
            telegram_id сохраненного пользователя (в виде строки)
        """
        async with SESSION_FACTORY() as session:
            added_user = UserMapper.to_entity(user)
            session.add(added_user)
            await session.commit()
            await session.refresh(added_user)
            return str(added_user.telegram_id)

    async def get_user(self, telegram_id: int) -> Optional[User]:
        """
        Метод асинхронно получает пользователя из базы данных

        :return:
            объект пользователя с метаинформацией
        """
        async with SESSION_FACTORY() as session:
            user = await session.get(UsersORM, telegram_id)
            return UserMapper.to_dto(user) if user else None

    async def get_users_by_type(self, user_type: USER_TYPE) -> List[User]:
        """
        Метод для получения всех пользователей определенного типа
        :param user_type: тип, пользователей которого будет возвращен
        :return: список пользователей
        """
        async with SESSION_FACTORY() as session:
            result = await session.scalars(
                select(UsersORM).where(UsersORM.user_type == user_type)
            )
            users = result.all()
            return [UserMapper.to_dto(user) for user in users]

    async def get_users(self) -> List[User]:
        """
        Метод для получения всех пользователей
        :return: список пользователей
        """
        async with SESSION_FACTORY() as session:
            result = await session.scalars(select(UsersORM))
            users = result.all()
            return [UserMapper.to_dto(user) for user in users]

    async def update_user(self, user: User) -> None:
        """
        Метод для обновления информации о пользователе. Значение будет обновлено только если пользователь есть в базе
        :param user: объект пользователя
        :return:
        """
        async with SESSION_FACTORY() as session:
            db_user = await session.get(UsersORM, user.telegram_id)
            if db_user:
                updated_user = UserMapper.to_entity(user)
                updated_user = await session.merge(updated_user)
                await session.commit()
                await session.refresh(updated_user)

