
from db.postgres_models import SurveyORM
from dtos import Survey
from mappers.abc_mapper import ABCMapper


class SurveyMapper(ABCMapper):
    @staticmethod
    def to_dto(entity: SurveyORM):
        return Survey(
            id=entity.id,
            name=entity.name
        )

    @staticmethod
    def to_entity(dto: Survey):
        return SurveyORM(
            id=dto.id,
            name=dto.name
        )