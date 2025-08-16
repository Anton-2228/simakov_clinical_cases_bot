from pydantic import BaseModel
from db.postgres import Base


class ABCMapper:
    """
    Класс для каста dto в entity и обратно
    """

    @staticmethod
    def to_dto(entity: Base):
        pass

    @staticmethod
    def to_entity(dto: BaseModel):
        pass