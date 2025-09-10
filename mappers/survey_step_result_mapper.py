from datetime import datetime

from db.postgres_models import SurveyStepResultORM
from dtos import SurveyStepResult
from mappers.abc_mapper import ABCMapper
from mappers.survey_step_mapper import SurveyStepMapper


class SurveyStepResultMapper(ABCMapper):
    @staticmethod
    def to_dto(entity: SurveyStepResultORM):
        return SurveyStepResult(
            id=entity.id,
            survey_step_id=entity.survey_step_id,
            result=entity.result,
            created_at=entity.created_at,
            survey_result_id=entity.survey_result_id
        )

    @staticmethod
    def to_entity(dto: SurveyStepResult):
        return SurveyStepResultORM(
            id=dto.id,
            survey_step_id=dto.survey_step_id,
            result=dto.result,
            created_at=dto.created_at or None,
            survey_result_id=dto.survey_result_id
        )
