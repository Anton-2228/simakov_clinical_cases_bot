from datetime import datetime
from typing import TYPE_CHECKING

from db.postgres_models import SurveyResultORM
from dtos import SurveyResult
from mappers.abc_mapper import ABCMapper

if TYPE_CHECKING:
    from mappers.survey_mapper import SurveyMapper
    from mappers.survey_step_result_mapper import SurveyStepResultMapper


class SurveyResultMapper(ABCMapper):
    @staticmethod
    def to_dto(entity: SurveyResultORM):
        from mappers.survey_mapper import SurveyMapper
        from mappers.survey_step_result_mapper import SurveyStepResultMapper
        
        survey_step_results = None
        if entity.survey_step_results:
            survey_step_results = [
                SurveyStepResultMapper.to_dto(step_result) 
                for step_result in entity.survey_step_results
            ]
        
        survey = None
        if entity.survey:
            survey = SurveyMapper.to_dto(entity.survey)
        
        return SurveyResult(
            id=entity.id,
            user_id=entity.user_id,
            survey_id=entity.survey_id,
            created_at=entity.created_at,
            survey=survey,
            survey_step_results=survey_step_results
        )

    @staticmethod
    def to_entity(dto: SurveyResult):
        return SurveyResultORM(
            id=dto.id,
            user_id=dto.user_id,
            survey_id=dto.survey_id,
            created_at=dto.created_at or datetime.utcnow()
        )
