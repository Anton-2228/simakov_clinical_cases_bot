from models import User
from resources.messages import EDIT_ADMIN_LIST_MESSAGE, EDIT_SURVEY


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
    text_message = ("Для редактирования шага выберите его\n\n"
                    "Шаги опроса:\n")
    for x, step in enumerate(survey_steps):
        message_part = EDIT_SURVEY.format(id=step["id"],
                                          name=step["name"],
                                          type=step["type"])
        text_message += f"{message_part}\n"
        if x + 1 != len(survey_steps):
            text_message += "------------------\n"

    return text_message
