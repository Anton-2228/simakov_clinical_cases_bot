from typing import Optional

from pydantic import BaseModel

from enums import SURVEY_STEP_TYPE


class Survey(BaseModel):
    id: Optional[int] = None
    name: str


class SurveyStep(BaseModel):
    id: Optional[int] = None
    survey: Survey
    name: str
    position: int
    text: str
    type: SURVEY_STEP_TYPE
