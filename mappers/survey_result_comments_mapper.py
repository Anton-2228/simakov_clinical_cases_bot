from datetime import datetime
from typing import TYPE_CHECKING

from db.postgres_models import SurveyResultCommentsORM
from dtos import SurveyResultComments
from mappers.abc_mapper import ABCMapper

if TYPE_CHECKING:
    pass


class SurveyResultCommentsMapper(ABCMapper):
    @staticmethod
    def to_dto(entity: SurveyResultCommentsORM):
        return SurveyResultComments(
            id=entity.id,
            survey_result_id=entity.survey_result_id,
            type=entity.type,
            result=entity.result,
            created_at=entity.created_at
        )

    @staticmethod
    def to_entity(dto: SurveyResultComments):
        return SurveyResultCommentsORM(
            id=dto.id,
            survey_result_id=dto.survey_result_id,
            type=dto.type,
            result=dto.result
            # created_at=dto.created_at or datetime.utcnow()
        )
