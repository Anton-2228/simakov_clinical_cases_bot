from abc import ABC, abstractmethod

from pydantic import BaseModel

from db.postgres import Base


class ABCMapper(ABC):
    """
    Класс для каста dto в entity и обратно
    """

    @staticmethod
    @abstractmethod
    def to_dto(entity: Base):
        pass

    @staticmethod
    @abstractmethod
    def to_entity(dto: BaseModel):
        pass