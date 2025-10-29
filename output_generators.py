import json

from dtos import SurveyStep, SurveyStepResult, SurveyResult, SurveyResultComments
from enums import SURVEY_STEP_TYPE, SURVEY_RESULT_COMMENT_TYPE
from models import User
from resources.messages import (ADD_SURVEY_STEP,
                                CHANGE_SURVEY_STEP_CURRENT_STEP_DATA,
                                EDIT_ADMIN_LIST_MESSAGE, EDIT_SURVEY,
                                SET_STEPS_ORDER, TAKE_SURVEY_COUNT_FILES,
                                TAKE_SURVEY_ENTER_FILES,
                                TAKE_SURVEY_ENTER_STRING, ADD_SURVEY, CHANGE_SURVEY_CURRENT_SURVEY_DATA,
                                MESSAGE_TO_ADMINS, MESSAGE_TO_USER, SEND_MESSAGE_TO_USER, SEND_MESSAGE_TO_ALL_USERS,
                                SEND_MESSAGE_TO_ALL_USERS_FINISH, SEE_ANSWERS_STRING,
                                SEE_ANSWERS_FILES,
                                SEND_INFO_ABOUT_NEW_SURVEY_RESULT, ADD_FILES_TO_SURVEY_RESULT_COUNT_FILES,
                                SEE_COMMENTS_FILES, SEE_COMMENTS_STRING, TAKE_SURVEY_ENTER_YES_NO,
                                TAKE_SURVEY_ENTER_STRING_OR_FILES)
from utils import load_json


def create_edit_admin_list_output(admins: list[User]) -> str:
    text_message = "Текущий whitelist:\n"
    for x, admin in enumerate(admins):
        message_part = EDIT_ADMIN_LIST_MESSAGE.format(user_tg_id=admin.telegram_id,
                                                      user_name=admin.full_name)
        text_message += f"{message_part}\n"
        if x + 1 != len(admins):
            text_message += "------------------\n"

    return text_message

def create_edit_survey_output(survey_steps: list[dict]) -> str:
    text_message = "Для редактирования шага выберите его\n\n"
    text_message += "Шаги опроса представлены в том порядке, в каком пользователь будет их проходить:\n\n"
    for x, step in enumerate(survey_steps):
        message_part = EDIT_SURVEY.format(id=step["id"],
                                          name=step["name"],
                                          type=step["type"])
        text_message += f"{message_part}\n\n"
        text_message += "          ↓\n\n"
        # if x + 1 != len(survey_steps):
        #     text_message += "------------------\n"

    return text_message

def create_edit_survey_step_output(step: dict) -> str:
    text_message = CHANGE_SURVEY_STEP_CURRENT_STEP_DATA.format(id=step["id"],
                                                               name=step["name"],
                                                               text=step["text"],
                                                               type=step["type"])
    return text_message

def create_set_steps_order_output(survey_steps: list[dict]) -> str:
    text_message = ("Введите через пробел id шагов в том порядке, в котором они должны идти\n\n"
                    "Шаги опроса:\n")
    for x, step in enumerate(survey_steps):
        message_part = SET_STEPS_ORDER.format(id=step["id"],
                                              name=step["name"],
                                              type=step["type"])
        text_message += f"{message_part}\n"
        if x + 1 != len(survey_steps):
            text_message += "------------------\n"

    return text_message

def create_add_survey_step_output() -> str:
    text_message = ADD_SURVEY_STEP
    return text_message

def create_add_survey_output() -> str:
    text_message = ADD_SURVEY
    return text_message

def create_take_survey_step_output(step_type: SURVEY_STEP_TYPE, step_text: str) -> str:
    text_message = None
    if step_type == SURVEY_STEP_TYPE.STRING:
        text_message = TAKE_SURVEY_ENTER_STRING.format(step_text=step_text)
    elif step_type == SURVEY_STEP_TYPE.FILES:
        text_message = TAKE_SURVEY_ENTER_FILES.format(step_text=step_text)
    elif step_type == SURVEY_STEP_TYPE.YES_NO:
        text_message = TAKE_SURVEY_ENTER_YES_NO.format(step_text=step_text)
    elif step_type == SURVEY_STEP_TYPE.STRING_OR_FILES:
        text_message = TAKE_SURVEY_ENTER_STRING_OR_FILES.format(step_text=step_text)
    assert text_message is not None, f"Нет генератора сообщения для типа ответа {step_type}"
    return text_message

def create_take_survey_file_count_output(file_count) -> str:
    text_message = TAKE_SURVEY_COUNT_FILES.format(file_count=file_count)
    return text_message

def create_change_survey_output(survey: dict) -> str:
    text_message = CHANGE_SURVEY_CURRENT_SURVEY_DATA.format(name=survey["name"],
                                                            start_message=survey["start_message"],
                                                            finish_message=survey["finish_message"])
    return text_message

def create_message_to_admins_output(user: User) -> str:
    return MESSAGE_TO_ADMINS.format(user_name=f"{user.full_name}(ID: {user.telegram_id})")

def create_send_message_to_user_output(user: User) -> str:
    return SEND_MESSAGE_TO_USER.format(user_name=f"{user.full_name}(ID: {user.telegram_id})")

def create_send_message_to_all_users_output() -> str:
    return SEND_MESSAGE_TO_ALL_USERS

def create_survey_result_see_answers_output(step: SurveyStep, step_result: SurveyStepResult) -> str:
    text_message = None
    if step.type == SURVEY_STEP_TYPE.STRING:
        answer = json.loads(step_result.result)
        text_message = SEE_ANSWERS_STRING.format(ask=step.text,
                                                 answer=answer["answer"])
    elif step.type == SURVEY_STEP_TYPE.FILES:
        text_message = SEE_ANSWERS_FILES.format(ask=step.text)
    assert text_message is not None, f"Нет генератора сообщения для типа ответа {step.type}"
    return text_message

def create_survey_result_comments_see_answers_output(survey_result_comment: SurveyResultComments) -> str:
    text_message = None
    if survey_result_comment.type == SURVEY_RESULT_COMMENT_TYPE.STRING:
        answer = json.loads(survey_result_comment.result)
        text_message = SEE_COMMENTS_STRING.format(created_at=survey_result_comment.created_at,
                                                  comment=answer["answer"])
    elif survey_result_comment.type == SURVEY_RESULT_COMMENT_TYPE.FILES:
        text_message = SEE_COMMENTS_FILES.format(created_at=survey_result_comment.created_at)
    assert text_message is not None, f"Нет генератора сообщения для типа комментария {survey_result_comment.type}"
    return text_message

def create_add_files_to_survey_result_file_count_output(file_count) -> str:
    text_message = ADD_FILES_TO_SURVEY_RESULT_COUNT_FILES.format(file_count=file_count)
    return text_message

def create_send_info_about_new_survey_result_output(user: User, survey_result: SurveyResult) -> str:
    text_message = SEND_INFO_ABOUT_NEW_SURVEY_RESULT.format(name=f"{user.full_name}(ID: {user.telegram_id})",
                                                            survey_name=survey_result.survey.name)
    return text_message

def create_unprocessed_survey_results_output(survey_results: list) -> str:
    text_message = "Необработанные результаты опросов:\n\n"
    for i, survey_result in enumerate(survey_results, 1):
        text_message += f"{i}.\n"
        text_message += f"Имя: {survey_result['full_name']}\n"
        text_message += f"ID: {survey_result['telegram_id']}\n"
        text_message += f"Опрос: {survey_result['survey_name']}\n\n"
    return text_message
