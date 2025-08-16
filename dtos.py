from pydantic import BaseModel

from enums import SURVEY_STEP_TYPE

from typing import TYPE_CHECKING, Optional


class Survey(BaseModel):
    id: Optional[int] = None
    name: str


class SurveyStep(BaseModel):
    id: Optional[int] = None
    survey: Survey
    name: str
    position: int
    type: SURVEY_STEP_TYPE
