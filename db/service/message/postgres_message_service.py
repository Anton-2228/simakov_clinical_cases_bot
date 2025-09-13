from typing import List, Optional

from sqlalchemy import select

from db.postgres import SESSION_FACTORY
from db.postgres_models import MessagesORM
from db.service.message.async_message_service import AsyncMessageService
from dtos import Message
from mappers.message_mapper import MessageMapper


class PostgresMessageService(AsyncMessageService):
    async def save_message(self, message: Message) -> Message:
        async with SESSION_FACTORY() as session:
            added_message = MessageMapper.to_entity(message)
            session.add(added_message)
            await session.commit()
            await session.refresh(added_message)
            return MessageMapper.to_dto(added_message)

    async def get_all_messages(self) -> List[Message]:
        async with SESSION_FACTORY() as session:
            result = await session.scalars(select(MessagesORM))
            messages = result.all()
            return [MessageMapper.to_dto(message) for message in messages]

    async def get_message(self, id: int) -> Optional[Message]:
        async with SESSION_FACTORY() as session:
            message = await session.get(MessagesORM, id)
            return MessageMapper.to_dto(message) if message else None

    async def update_message(self, message: Message) -> Message:
        async with SESSION_FACTORY() as session:
            updated_message = MessageMapper.to_entity(message)
            updated_message = await session.merge(updated_message)
            await session.commit()
            await session.refresh(updated_message)
            return MessageMapper.to_dto(updated_message)

    async def delete_message(self, id: int) -> None:
        async with SESSION_FACTORY() as session:
            message = await session.get(MessagesORM, id)
            await session.delete(message)
            await session.commit()

    async def get_messages_by_user(self, user_id: int) -> List[Message]:
        async with SESSION_FACTORY() as session:
            result = await session.scalars(
                select(MessagesORM).where(MessagesORM.to_user_id == user_id)
            )
            messages = result.all()
            return [MessageMapper.to_dto(message) for message in messages]

    async def get_messages_by_status(self, status: "MessageStatus") -> List[Message]:
        async with SESSION_FACTORY() as session:
            result = await session.scalars(
                select(MessagesORM).where(MessagesORM.status == status)
            )
            messages = result.all()
            return [MessageMapper.to_dto(message) for message in messages]

    async def get_messages_by_type(self, message_type: "MESSAGE_TYPE") -> List[Message]:
        async with SESSION_FACTORY() as session:
            result = await session.scalars(
                select(MessagesORM).where(MessagesORM.type == message_type)
            )
            messages = result.all()
            return [MessageMapper.to_dto(message) for message in messages]

    async def get_messages_by_type_and_status(self, message_type: "MESSAGE_TYPE", status: "MessageStatus") -> List[Message]:
        async with SESSION_FACTORY() as session:
            result = await session.scalars(
                select(MessagesORM).where(
                    MessagesORM.type == message_type,
                    MessagesORM.status == status
                )
            )
            messages = result.all()
            return [MessageMapper.to_dto(message) for message in messages]
