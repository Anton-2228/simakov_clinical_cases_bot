from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks_factories import UserMainMenuCallbackFactory, AdminMainMenuCallbackFactory, EditAdminListCallbackFactory, \
    AddUserToAdminListCallbackFactory, DeleteUserFromAdminListCallbackFactory, EditSurveyCallbackFactory, \
    EditSurveysCallbackFactory, AddSurveyCallbackFactory, ChangeSurveyStepsCallbackFactory, \
    SetStepsOrderCallbackFactory, \
    AddSurveyStepCallbackFactory, SelectTakeSurveyCallbackFactory, EditSurveyStepsCallbackFactory, \
    TakeSurveyCallbackFactory
from enums import ListUserMainMenuActions, ListAdminMainMenuActions, ListEditAdminListActions, \
    ListAddUserToAdminListActions, ListDeleteUserFromAdminListActions, ListEditSurveyActions, ListEditSurveysActions, \
    ListAddSurveyListActions, ListChangeSurveyStepsActions, SURVEY_STEP_VARIABLE_FILEDS, SURVEY_STEP_TYPE, \
    ListSetStepsOrderActions, ListAddSurveyStepActions, ListSelectTakeSurveyActions, ListTakeSurveyActions, \
    ListEditSurveyStepsActions
from models import User
from pagers.pager import PAGING_STATUS


def get_keyboard_for_user_main_menu() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="Пройти опрос", callback_data=UserMainMenuCallbackFactory(action=ListUserMainMenuActions.TAKE_THE_SURVEY))
    builder.adjust(1)
    return builder

def get_keyboard_for_admin_main_menu() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="Пройти опрос", callback_data=AdminMainMenuCallbackFactory(action=ListAdminMainMenuActions.TAKE_THE_SURVEY))
    builder.button(text="Отредактировать опросы", callback_data=AdminMainMenuCallbackFactory(action=ListAdminMainMenuActions.EDIT_SURVEYS))
    builder.button(text="Обновить список админов", callback_data=AdminMainMenuCallbackFactory(action=ListAdminMainMenuActions.EDIT_ADMIN_LIST))
    builder.adjust(1)
    return builder

def get_keyboard_for_edit_admin_list() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="Добавить админа", callback_data=EditAdminListCallbackFactory(action=ListEditAdminListActions.ADD_ADMIN))
    builder.button(text="Удалить админа", callback_data=EditAdminListCallbackFactory(action=ListEditAdminListActions.REMOVE_ADMIN))
    builder.button(text="Вернуться в главное меню", callback_data=EditAdminListCallbackFactory(action=ListEditAdminListActions.RETURN_TO_MAIN_MENU))
    builder.adjust(2, 1)
    return builder

def get_keyboard_for_add_user_to_admin_list() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Вернуться", callback_data=AddUserToAdminListCallbackFactory(action=ListAddUserToAdminListActions.RETURN_TO_EDIT_ADMIN_LIST).pack()))
    builder.adjust(1)
    return builder

def get_keyboard_for_remove_admins(admins: list[User]) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for admin in admins:
        builder.button(text=str(admin.telegram_id), callback_data=DeleteUserFromAdminListCallbackFactory(action=ListDeleteUserFromAdminListActions.DELETION_SELECTION,
                                                                                                         user_id=admin.telegram_id))
    builder.adjust(3, repeat=True)
    builder.row(InlineKeyboardButton(text="Вернуться", callback_data=DeleteUserFromAdminListCallbackFactory(action=ListDeleteUserFromAdminListActions.RETURN_TO_EDIT_ADMIN_LIST).pack()))
    return builder

def get_keyboard_for_edit_surveys(surveys: list[str], survey_idx_map: dict[int, str], page_status: PAGING_STATUS) -> InlineKeyboardBuilder:
    def _get_survey_id(survey_name: str):
        for id in survey_idx_map:
            if survey_idx_map[id] == survey_name:
                return id

    builder = InlineKeyboardBuilder()
    for survey in surveys:
        survey_id = _get_survey_id(survey_name=survey)
        builder.button(
            text=survey,
            callback_data=EditSurveysCallbackFactory(
                action=ListEditSurveysActions.EDIT_SELECTION,
                survey_id=survey_id
            )
        )

    builder.adjust(1, repeat=True)

    navigate_buttons = []
    if page_status not in [PAGING_STATUS.FIRST_PAGE, PAGING_STATUS.ONLY_PAGE, PAGING_STATUS.NO_PAGE]:
        previous_button = InlineKeyboardButton(
            text="Назад",
            callback_data=EditSurveysCallbackFactory(action=ListEditSurveysActions.PREVIOUS_SURVEYS).pack())
        navigate_buttons.append(previous_button)
    if page_status not in [PAGING_STATUS.LAST_PAGE, PAGING_STATUS.ONLY_PAGE, PAGING_STATUS.NO_PAGE]:
        next_button = InlineKeyboardButton(
            text="Вперед",
            callback_data=EditSurveysCallbackFactory(action=ListEditSurveysActions.NEXT_SURVEYS).pack())
        navigate_buttons.append(next_button)
    builder.row(*navigate_buttons)

    add_new_survey_button = InlineKeyboardButton(
        text="Добавить новый опрос",
        callback_data=EditSurveysCallbackFactory(action=ListEditSurveysActions.ADD_SURVEY).pack()
    )
    builder.row(add_new_survey_button)
    return_to_main_menu_button = InlineKeyboardButton(
        text="Вернуться в главное меню",
        callback_data=EditSurveysCallbackFactory(action=ListEditSurveysActions.RETURN_TO_MAIN_MENU).pack()
    )
    builder.row(return_to_main_menu_button)
    return builder

def get_keyboard_for_edit_survey(steps_idx: list[int], page_status: PAGING_STATUS) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for step_id in steps_idx:
        builder.button(
            text=str(step_id),
            callback_data=EditSurveyCallbackFactory(
                action=ListEditSurveyActions.EDIT_SELECTION,
                step_id=step_id
            )
        )

    builder.adjust(6, repeat=True)

    navigate_buttons = []
    if page_status not in [PAGING_STATUS.FIRST_PAGE, PAGING_STATUS.ONLY_PAGE, PAGING_STATUS.NO_PAGE]:
        previous_button = InlineKeyboardButton(
            text="Назад",
            callback_data=EditSurveyCallbackFactory(action=ListEditSurveyActions.PREVIOUS_STEPS).pack())
        navigate_buttons.append(previous_button)
    if page_status not in [PAGING_STATUS.LAST_PAGE, PAGING_STATUS.ONLY_PAGE, PAGING_STATUS.NO_PAGE]:
        next_button = InlineKeyboardButton(
            text="Вперед",
            callback_data=EditSurveyCallbackFactory(action=ListEditSurveyActions.NEXT_STEPS).pack())
        navigate_buttons.append(next_button)
    builder.row(*navigate_buttons)

    add_new_step_button = InlineKeyboardButton(
        text="Добавить новый шаг опроса",
        callback_data=EditSurveyCallbackFactory(action=ListEditSurveyActions.ADD_NEW_STEP).pack()
    )
    builder.row(add_new_step_button)
    set_steps_order_button = InlineKeyboardButton(
        text="Изменить порядок шагов",
        callback_data=EditSurveyCallbackFactory(action=ListEditSurveyActions.SET_STEPS_ORDER).pack()
    )
    builder.row(set_steps_order_button)
    delete_survey_button = InlineKeyboardButton(
        text="Удалить опрос",
        callback_data=EditSurveyCallbackFactory(action=ListEditSurveyActions.DELETE_SURVEY).pack()
    )
    builder.row(delete_survey_button)
    return_button = InlineKeyboardButton(
        text="Вернуться",
        callback_data=EditSurveyCallbackFactory(action=ListEditSurveyActions.RETURN).pack()
    )
    builder.row(return_button)
    return builder

def get_keyboard_for_add_survey() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Вернуться", callback_data=AddSurveyCallbackFactory(action=ListAddSurveyListActions.RETURN_TO_EDIT_SURVEYS).pack()))
    builder.adjust(1)
    return builder

def get_keyboard_for_change_survey_steps(field: SURVEY_STEP_VARIABLE_FILEDS) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    if field == SURVEY_STEP_VARIABLE_FILEDS.TYPE:
        str_button = InlineKeyboardButton(text="Текст",
                                          callback_data=ChangeSurveyStepsCallbackFactory(
                                              action=ListChangeSurveyStepsActions.SELECT_STEP_TYPE,
                                              step_type=SURVEY_STEP_TYPE.STRING).pack()
                                          )
        files_button = InlineKeyboardButton(text="Файлы",
                                            callback_data=ChangeSurveyStepsCallbackFactory(
                                                action=ListChangeSurveyStepsActions.SELECT_STEP_TYPE,
                                                step_type=SURVEY_STEP_TYPE.FILES).pack()
                                            )

        builder.row(str_button, files_button)
    builder.row(InlineKeyboardButton(text="Оставить текущее", callback_data=ChangeSurveyStepsCallbackFactory(action=ListChangeSurveyStepsActions.KEEP_CURRENT_VALUE).pack()))
    return builder

def get_keyboard_for_set_steps_order(page_status: PAGING_STATUS) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    navigate_buttons = []
    if page_status not in [PAGING_STATUS.FIRST_PAGE, PAGING_STATUS.ONLY_PAGE, PAGING_STATUS.NO_PAGE]:
        previous_button = InlineKeyboardButton(
            text="Назад",
            callback_data=SetStepsOrderCallbackFactory(action=ListSetStepsOrderActions.PREVIOUS_STEPS).pack())
        navigate_buttons.append(previous_button)
    if page_status not in [PAGING_STATUS.LAST_PAGE, PAGING_STATUS.ONLY_PAGE, PAGING_STATUS.NO_PAGE]:
        next_button = InlineKeyboardButton(
            text="Вперед",
            callback_data=SetStepsOrderCallbackFactory(action=ListSetStepsOrderActions.NEXT_STEPS).pack())
        navigate_buttons.append(next_button)
    builder.row(*navigate_buttons)

    keep_current_value_button = InlineKeyboardButton(
        text="Оставить текущий порядок",
        callback_data=SetStepsOrderCallbackFactory(action=ListSetStepsOrderActions.KEEP_CURRENT_VALUE).pack()
    )
    builder.row(keep_current_value_button)
    return builder

def get_keyboard_for_add_survey_steps(field: SURVEY_STEP_VARIABLE_FILEDS) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    if field == SURVEY_STEP_VARIABLE_FILEDS.TYPE:
        str_button = InlineKeyboardButton(text="Текст",
                                          callback_data=AddSurveyStepCallbackFactory(
                                              action=ListAddSurveyStepActions.SELECT_STEP_TYPE,
                                              step_type=SURVEY_STEP_TYPE.STRING).pack()
                                          )
        files_button = InlineKeyboardButton(text="Файлы",
                                            callback_data=AddSurveyStepCallbackFactory(
                                                action=ListAddSurveyStepActions.SELECT_STEP_TYPE,
                                                step_type=SURVEY_STEP_TYPE.FILES).pack()
                                            )

        builder.row(str_button, files_button)
    return builder

def get_keyboard_for_select_take_survey(surveys: list[str], survey_idx_map: dict[int, str], page_status: PAGING_STATUS) -> InlineKeyboardBuilder:
    def _get_survey_id(survey_name: str):
        for id in survey_idx_map:
            if survey_idx_map[id] == survey_name:
                return id

    builder = InlineKeyboardBuilder()
    for survey in surveys:
        survey_id = _get_survey_id(survey_name=survey)
        builder.button(
            text=survey,
            callback_data=SelectTakeSurveyCallbackFactory(
                action=ListSelectTakeSurveyActions.TAKE_SELECTION,
                survey_id=survey_id
            )
        )

    builder.adjust(1, repeat=True)

    navigate_buttons = []
    if page_status not in [PAGING_STATUS.FIRST_PAGE, PAGING_STATUS.ONLY_PAGE, PAGING_STATUS.NO_PAGE]:
        previous_button = InlineKeyboardButton(
            text="Назад",
            callback_data=SelectTakeSurveyCallbackFactory(action=ListSelectTakeSurveyActions.PREVIOUS_SURVEYS).pack())
        navigate_buttons.append(previous_button)
    if page_status not in [PAGING_STATUS.LAST_PAGE, PAGING_STATUS.ONLY_PAGE, PAGING_STATUS.NO_PAGE]:
        next_button = InlineKeyboardButton(
            text="Вперед",
            callback_data=SelectTakeSurveyCallbackFactory(action=ListSelectTakeSurveyActions.NEXT_SURVEYS).pack())
        navigate_buttons.append(next_button)
    builder.row(*navigate_buttons)

    return_to_main_menu_button = InlineKeyboardButton(
        text="Вернуться в главное меню",
        callback_data=SelectTakeSurveyCallbackFactory(action=ListSelectTakeSurveyActions.RETURN_TO_MAIN_MENU).pack()
    )
    builder.row(return_to_main_menu_button)
    return builder

def get_keyboard_for_take_survey() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    start_button = InlineKeyboardButton(
        text="Начать",
        callback_data=TakeSurveyCallbackFactory(action=ListTakeSurveyActions.START_SURVEY).pack()
    )
    builder.row(start_button)
    return_to_select_take_survey_button = InlineKeyboardButton(
        text="Вернуться к выбору опроса",
        callback_data=TakeSurveyCallbackFactory(action=ListTakeSurveyActions.RETURN_TO_SELECT_TAKE_SURVEY).pack()
    )
    builder.row(return_to_select_take_survey_button)
    return builder

def get_keyboard_for_take_survey_step(step_type: SURVEY_STEP_TYPE) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    if step_type == SURVEY_STEP_TYPE.FILES:
        finish_send_files_button = InlineKeyboardButton(
            text="Все файлы отправлены",
            callback_data=TakeSurveyCallbackFactory(action=ListTakeSurveyActions.FINISH_SEND_FILES).pack()
        )
        builder.row(finish_send_files_button)
    return_to_select_take_survey_button = InlineKeyboardButton(
        text="Преждевременно завершить опрос",
        callback_data=TakeSurveyCallbackFactory(action=ListTakeSurveyActions.RETURN_TO_SELECT_TAKE_SURVEY).pack()
    )
    builder.row(return_to_select_take_survey_button)
    return builder

def get_keyboard_for_confirm_delete_survey() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    confirm_delete_button = InlineKeyboardButton(
        text="Удалить опрос",
        callback_data=EditSurveyCallbackFactory(action=ListEditSurveyActions.CONFIRM_DELETE_SURVEY).pack()
    )
    builder.row(confirm_delete_button)
    return_button = InlineKeyboardButton(
        text="Вернуться",
        callback_data=EditSurveyCallbackFactory(action=ListEditSurveyActions.REJECT_DELETE_SURVEY).pack()
    )
    builder.row(return_button)
    return builder

def get_keyboard_for_edit_survey_step() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    change_step = InlineKeyboardButton(
        text="Редактировать шаг",
        callback_data=EditSurveyStepsCallbackFactory(action=ListEditSurveyStepsActions.CHANGE_STEP).pack()
    )
    builder.row(change_step)
    delete_button = InlineKeyboardButton(
        text="Удалить шаг",
        callback_data=EditSurveyStepsCallbackFactory(action=ListEditSurveyStepsActions.DELETE_STEP).pack()
    )
    builder.row(delete_button)
    return_button = InlineKeyboardButton(
        text="Вернуться",
        callback_data=EditSurveyStepsCallbackFactory(action=ListEditSurveyStepsActions.RETURN_TO_EDIT_SURVEY).pack()
    )
    builder.row(return_button)
    return builder

def get_keyboard_for_confirm_delete_step() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    confirm_delete_button = InlineKeyboardButton(
        text="Удалить шаг",
        callback_data=EditSurveyStepsCallbackFactory(action=ListEditSurveyStepsActions.CONFIRM_DELETE_STEP).pack()
    )
    builder.row(confirm_delete_button)
    return_button = InlineKeyboardButton(
        text="Вернуться",
        callback_data=EditSurveyStepsCallbackFactory(action=ListEditSurveyStepsActions.REJECT_DELETE_STEP).pack()
    )
    builder.row(return_button)
    return builder
