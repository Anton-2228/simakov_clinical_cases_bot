from db.postgres_models import MessagesORM
from dtos import Message
from mappers.abc_mapper import ABCMapper


class MessageMapper(ABCMapper):
    @staticmethod
    def to_dto(entity: MessagesORM):
        return Message(
            id=entity.id,
            text=entity.text,
            from_user_id=entity.from_user_id,
            to_user_id=entity.to_user_id,
            status=entity.status,
            type=entity.type
        )

    @staticmethod
    def to_entity(dto: Message):
        return MessagesORM(
            id=dto.id,
            text=dto.text,
            from_user_id=dto.from_user_id,
            to_user_id=dto.to_user_id,
            status=dto.status,
            type=dto.type
        )