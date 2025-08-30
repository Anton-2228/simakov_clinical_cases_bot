
from db.postgres_models import SurveyStepORM
from dtos import SurveyStep
from mappers.abc_mapper import ABCMapper
from mappers.survey_mapper import SurveyMapper


class SurveyStepMapper(ABCMapper):
    @staticmethod
    def to_dto(entity: SurveyStepORM):
        return SurveyStep(
            id=entity.id,
            name=entity.name,
            position=entity.position,
            type=entity.type,
            text=entity.text,
            # survey_id=entity.survey_id
            survey=SurveyMapper.to_dto(entity.survey)
        )

    @staticmethod
    def to_entity(dto: SurveyStep):
        return SurveyStepORM(
            id=dto.id,
            name=dto.name,
            position=dto.position,
            type=dto.type,
            text=dto.text,
            survey_id=dto.survey.id
            # survey=SurveyMapper.to_entity(dto.survey)
        )