
from db.postgres_models import SurveyStepORM
from dtos import SurveyStep
from mappers.abc_mapper import ABCMapper


class SurveyStepMapper(ABCMapper):
    @staticmethod
    def to_dto(entity: SurveyStepORM):
        return SurveyStep(
            id=entity.id,
            name=entity.name,
            position=entity.position,
            type=entity.type,
            text=entity.text,
            image=entity.image,
            survey_id=entity.survey_id
        )

    @staticmethod
    def to_entity(dto: SurveyStep):
        return SurveyStepORM(
            id=dto.id,
            name=dto.name,
            position=dto.position,
            type=dto.type,
            text=dto.text,
            image=dto.image,
            survey_id=dto.survey_id
        )