
from typing import TYPE_CHECKING

from db.postgres_models import SurveyORM
from dtos import Survey
from mappers.abc_mapper import ABCMapper

if TYPE_CHECKING:
    from mappers.survey_step_mapper import SurveyStepMapper


class SurveyMapper(ABCMapper):
    @staticmethod
    def to_dto(entity: SurveyORM):
        survey_steps = None
        if entity.survey_steps:
            from mappers.survey_step_mapper import SurveyStepMapper
            survey_steps = [
                SurveyStepMapper.to_dto(step) 
                for step in entity.survey_steps
            ]
        
        return Survey(
            id=entity.id,
            name=entity.name,
            start_message=entity.start_message,
            finish_message=entity.finish_message,
            survey_steps=survey_steps
        )

    @staticmethod
    def to_entity(dto: Survey):
        return SurveyORM(
            id=dto.id,
            name=dto.name,
            start_message=dto.start_message,
            finish_message=dto.finish_message,
        )