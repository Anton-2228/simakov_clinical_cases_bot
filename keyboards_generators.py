from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from callbacks_factories import (AddSurveyCallbackFactory,
                                 AddSurveyStepCallbackFactory,
                                 AddUserToAdminListCallbackFactory,
                                 AdminMainMenuCallbackFactory,
                                 ChangeSurveyCallbackFactory,
                                 ChangeSurveyStepsCallbackFactory,
                                 DeleteUserFromAdminListCallbackFactory,
                                 EditAdminListCallbackFactory,
                                 EditSurveyCallbackFactory,
                                 EditSurveysCallbackFactory,
                                 EditSurveyStepsCallbackFactory,
                                 SelectTakeSurveyCallbackFactory,
                                 SetStepsOrderCallbackFactory,
                                 SurveyActionsCallbackFactory,
                                 TakeSurveyCallbackFactory,
                                 UserMainMenuCallbackFactory, SendMessageToAdminCallbackFactory,
                                 ReplyMessageToClientCallbackFactory, SendMessageToUserCallbackFactory,
                                 SendMessageToAllUsersCallbackFactory,
                                 SelectUserToSendMessageCallbackFactory, SelectSurveyResultCallbackFactory,
                                 SurveyResultActionsCallbackFactory, AddCommentsCallbackFactory,
                                 AddFilesCallbackFactory, UnprocessedSurveyResultsCallbackFactory,
                                 UnprocessedSurveyResultCallbackFactory)
from enums import (SURVEY_STEP_TYPE, SURVEY_STEP_VARIABLE_FILEDS, SURVEY_VARIABLE_FIELDS,
                   ListAddSurveyListActions, ListAddSurveyStepActions,
                   ListAddUserToAdminListActions, ListAdminMainMenuActions,
                   ListChangeSurveyStepsActions,
                   ListDeleteUserFromAdminListActions,
                   ListEditAdminListActions, ListEditSurveyActions,
                   ListEditSurveysActions, ListEditSurveyStepsActions,
                   ListSelectTakeSurveyActions, ListSetStepsOrderActions,
                   ListSurveyActionsActions, ListTakeSurveyActions, ListUserMainMenuActions, ListChangeSurveyActions,
                   ListSendMessageToAdminActions, ListReplyMessageToClientActions, ListSendMessageToUserActions,
                   ListSendMessageToAllUsersActions,
                   ListSelectUserToSendMessageActions, ListSelectSurveyResultActions, ListSurveyResultActionsActions,
                   ListAddCommentsActions, ListAddFilesActions, ListUnprocessedSurveyResultsActions,
                   ListUnprocessedSurveyResultActions, YES_NO)
from models import User
from pagers.pager import PAGING_STATUS


def get_keyboard_for_user_main_menu() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="Отправить клинический случай", callback_data=UserMainMenuCallbackFactory(action=ListUserMainMenuActions.TAKE_THE_SURVEY))
    builder.button(text="Написать в поддержку", callback_data=UserMainMenuCallbackFactory(action=ListUserMainMenuActions.SEND_MESSAGE_TO_ADMIN))
    builder.adjust(1)
    return builder

def get_keyboard_for_admin_main_menu() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="Отправить клинический случай", callback_data=AdminMainMenuCallbackFactory(action=ListAdminMainMenuActions.TAKE_THE_SURVEY))
    builder.button(text="Отредактировать опросы", callback_data=AdminMainMenuCallbackFactory(action=ListAdminMainMenuActions.EDIT_SURVEYS))
    builder.button(text="Обновить список админов", callback_data=AdminMainMenuCallbackFactory(action=ListAdminMainMenuActions.EDIT_ADMIN_LIST))
    builder.button(text="Получить таблицу с пользователями", callback_data=AdminMainMenuCallbackFactory(action=ListAdminMainMenuActions.GET_DUMP_USERS))
    builder.button(text="Написать сообщение пользователю", callback_data=AdminMainMenuCallbackFactory(action=ListAdminMainMenuActions.SEND_MESSAGE_TO_USER))
    builder.button(text="Необработанные результаты опросов", callback_data=AdminMainMenuCallbackFactory(action=ListAdminMainMenuActions.UNPROCESSED_SURVEY_RESULTS))
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
    add_new_step_button = InlineKeyboardButton(
        text="Отредактировать опрос",
        callback_data=EditSurveyCallbackFactory(action=ListEditSurveyActions.CHANGE_SURVEY).pack()
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
        str_or_files_button = InlineKeyboardButton(text="Текст или Файлы",
                                                   callback_data=ChangeSurveyStepsCallbackFactory(
                                                       action=ListChangeSurveyStepsActions.SELECT_STEP_TYPE,
                                                       step_type=SURVEY_STEP_TYPE.STRING_OR_FILES).pack()
                                                   )
        builder.row(str_or_files_button)
        yes_no_button = InlineKeyboardButton(text="Да/Нет",
                                             callback_data=ChangeSurveyStepsCallbackFactory(
                                                action=ListChangeSurveyStepsActions.SELECT_STEP_TYPE,
                                                step_type=SURVEY_STEP_TYPE.YES_NO).pack()
                                            )
        yes_button = InlineKeyboardButton(text="Да",
                                             callback_data=ChangeSurveyStepsCallbackFactory(
                                                action=ListChangeSurveyStepsActions.SELECT_STEP_TYPE,
                                                step_type=SURVEY_STEP_TYPE.YES).pack()
                                            )

        builder.row(yes_no_button, yes_button)
    elif field == SURVEY_STEP_VARIABLE_FILEDS.IMAGE:
        not_necessary_button = InlineKeyboardButton(text="Изображение не нужно",
                                                    callback_data=ChangeSurveyStepsCallbackFactory(
                                                        action=ListChangeSurveyStepsActions.NOT_NECESSARY_IMAGE
                                                    ).pack()
                                                    )
        builder.row(not_necessary_button)
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
        str_or_files_button = InlineKeyboardButton(text="Текст или Файлы",
                                                   callback_data=AddSurveyStepCallbackFactory(
                                                       action=ListAddSurveyStepActions.SELECT_STEP_TYPE,
                                                       step_type=SURVEY_STEP_TYPE.STRING_OR_FILES).pack()
                                                   )
        builder.row(str_or_files_button)
        yes_no_button = InlineKeyboardButton(text="Да/Нет",
                                             callback_data=AddSurveyStepCallbackFactory(
                                                action=ListAddSurveyStepActions.SELECT_STEP_TYPE,
                                                step_type=SURVEY_STEP_TYPE.YES_NO).pack()
                                            )
        yes_button = InlineKeyboardButton(text="Да",
                                             callback_data=AddSurveyStepCallbackFactory(
                                                action=ListAddSurveyStepActions.SELECT_STEP_TYPE,
                                                step_type=SURVEY_STEP_TYPE.YES).pack()
                                            )

        builder.row(yes_no_button, yes_button)
    elif field == SURVEY_STEP_VARIABLE_FILEDS.IMAGE:
        not_necessary_button = InlineKeyboardButton(text="Изображение не нужно",
                                                    callback_data=AddSurveyStepCallbackFactory(
                                                        action=ListAddSurveyStepActions.NOT_NECESSARY_IMAGE
                                                    ).pack()
                                                    )
        builder.row(not_necessary_button)
    return builder

def get_keyboard_for_add_survey_field(field: SURVEY_VARIABLE_FIELDS) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    # Для полей опроса не нужны специальные кнопки, только кнопка "Вернуться"
    builder.row(InlineKeyboardButton(text="Прекратить создание опроса", callback_data=AddSurveyCallbackFactory(action=ListAddSurveyListActions.RETURN_TO_EDIT_SURVEYS).pack()))
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

def get_keyboard_for_take_survey_step(step_type: SURVEY_STEP_TYPE) -> tuple[InlineKeyboardBuilder, ReplyKeyboardBuilder | None]:
    builder = InlineKeyboardBuilder()

    reply_kb = None
    if step_type == SURVEY_STEP_TYPE.FILES:
        # reply_builder = ReplyKeyboardBuilder()
        # reply_builder.row(KeyboardButton(text="✅готово"))
        # reply_kb = reply_builder.as_markup(resize_keyboard=True)
        finish_send_files_button = InlineKeyboardButton(
            text="✅готово",
            callback_data=TakeSurveyCallbackFactory(action=ListTakeSurveyActions.FINISH_SEND_FILES).pack()
        )
        builder.row(finish_send_files_button)
    elif step_type == SURVEY_STEP_TYPE.STRING_OR_FILES:
        # reply_builder/ = ReplyKeyboardBuilder()
        # reply_builder.row(KeyboardButton(text="✅готово"))
        # reply_kb = reply_builder.as_markup(resize_keyboard=True)
        finish_send_files_button = InlineKeyboardButton(
            text="✅готово",
            callback_data=TakeSurveyCallbackFactory(action=ListTakeSurveyActions.FINISH_SEND_FILES).pack()
        )
        builder.row(finish_send_files_button)
    elif step_type == SURVEY_STEP_TYPE.YES_NO:
        yes_button = InlineKeyboardButton(
            text="Да",
            callback_data=TakeSurveyCallbackFactory(action=ListTakeSurveyActions.YES_NO_SELECTION,
                                                    yes_no_result=YES_NO.YES).pack()
        )
        no_button = InlineKeyboardButton(
            text="Нет",
            callback_data=TakeSurveyCallbackFactory(action=ListTakeSurveyActions.YES_NO_SELECTION,
                                                    yes_no_result=YES_NO.NO).pack()
        )
        builder.row(yes_button, no_button)
    elif step_type == SURVEY_STEP_TYPE.YES:
        yes_button = InlineKeyboardButton(
            text="Да",
            callback_data=TakeSurveyCallbackFactory(action=ListTakeSurveyActions.YES_NO_SELECTION,
                                                    yes_no_result=YES_NO.YES).pack()
        )
        builder.row(yes_button)

    return_to_select_take_survey_button = InlineKeyboardButton(
        text="В главное меню",
        callback_data=TakeSurveyCallbackFactory(action=ListTakeSurveyActions.RETURN_TO_SELECT_TAKE_SURVEY).pack()
    )
    builder.row(return_to_select_take_survey_button)

    return builder, reply_kb

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

def get_keyboard_for_change_survey(field: SURVEY_VARIABLE_FIELDS) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Оставить текущее", callback_data=ChangeSurveyCallbackFactory(action=ListChangeSurveyActions.KEEP_CURRENT_VALUE).pack()))
    return builder

def get_keyboard_for_send_message_to_admin() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Вернуться в главное меню", callback_data=SendMessageToAdminCallbackFactory(action=ListSendMessageToAdminActions.RETURN_TO_MAIN_MENU).pack()))
    return builder

def get_keyboard_for_reply_message_to_client(from_user_id: int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Ответить пользователю", callback_data=ReplyMessageToClientCallbackFactory(action=ListReplyMessageToClientActions.REPLY_TO_CLIENT,
                                                                                                                     from_user_id=from_user_id).pack()))
    return builder

def get_keyboard_for_send_message_to_user() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Вернуться в главное меню", callback_data=SendMessageToUserCallbackFactory(action=ListSendMessageToUserActions.RETURN_TO_MAIN_MENU).pack()))
    return builder

def get_keyboard_for_send_message_to_all_users() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Вернуться в главное меню", callback_data=SendMessageToAllUsersCallbackFactory(action=ListSendMessageToAllUsersActions.RETURN_TO_MAIN_MENU).pack()))
    return builder

def get_keyboard_for_select_user_to_send_message(users: list[str], user_idx_map: dict[int, str], page_status: PAGING_STATUS) -> InlineKeyboardBuilder:
    def _get_user_id(user_name: str):
        for id in user_idx_map:
            if user_idx_map[id] == user_name:
                return id

    builder = InlineKeyboardBuilder()
    for user in users:
        user_id = _get_user_id(user_name=user)
        builder.button(
            text=user,
            callback_data=SelectUserToSendMessageCallbackFactory(
                action=ListSelectUserToSendMessageActions.USER_SELECTION,
                user_id=user_id
            )
        )

    builder.adjust(1, repeat=True)

    navigate_buttons = []
    if page_status not in [PAGING_STATUS.FIRST_PAGE, PAGING_STATUS.ONLY_PAGE, PAGING_STATUS.NO_PAGE]:
        previous_button = InlineKeyboardButton(
            text="Назад",
            callback_data=SelectUserToSendMessageCallbackFactory(action=ListSelectUserToSendMessageActions.PREVIOUS_USERS).pack())
        navigate_buttons.append(previous_button)
    if page_status not in [PAGING_STATUS.LAST_PAGE, PAGING_STATUS.ONLY_PAGE, PAGING_STATUS.NO_PAGE]:
        next_button = InlineKeyboardButton(
            text="Вперед",
            callback_data=SelectUserToSendMessageCallbackFactory(action=ListSelectUserToSendMessageActions.NEXT_USERS).pack())
        navigate_buttons.append(next_button)
    builder.row(*navigate_buttons)

    send_to_all_users_button = InlineKeyboardButton(
        text="Отправить всем пользователям",
        callback_data=SelectUserToSendMessageCallbackFactory(action=ListSelectUserToSendMessageActions.SEND_TO_ALL_USERS).pack()
    )
    builder.row(send_to_all_users_button)

    return_to_main_menu_button = InlineKeyboardButton(
        text="Вернуться в главное меню",
        callback_data=SelectUserToSendMessageCallbackFactory(action=ListSelectUserToSendMessageActions.RETURN_TO_MAIN_MENU).pack()
    )
    builder.row(return_to_main_menu_button)
    return builder


def get_keyboard_for_survey_actions() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    
    take_survey_button = InlineKeyboardButton(
        text="Пройти опрос",
        callback_data=SurveyActionsCallbackFactory(action=ListSurveyActionsActions.TAKE_SURVEY).pack()
    )
    builder.row(take_survey_button)
    
    view_completed_button = InlineKeyboardButton(
        text="Просмотреть пройденные опросы",
        callback_data=SurveyActionsCallbackFactory(action=ListSurveyActionsActions.VIEW_COMPLETED_SURVEYS).pack()
    )
    builder.row(view_completed_button)
    
    return_to_main_menu_button = InlineKeyboardButton(
        text="Вернуться к выбору опроса",
        callback_data=SurveyActionsCallbackFactory(action=ListSurveyActionsActions.RETURN_TO_MAIN_MENU).pack()
    )
    builder.row(return_to_main_menu_button)
    
    return builder

def get_keyboard_for_select_survey_result(survey_results: list[str], survey_result_idx_map: dict[int, str], page_status: PAGING_STATUS) -> InlineKeyboardBuilder:
    def _get_survey_result_id(survey_result_text: str):
        for id in survey_result_idx_map:
            if survey_result_idx_map[id] == survey_result_text:
                return id

    builder = InlineKeyboardBuilder()
    for survey_result in survey_results:
        survey_result_id = _get_survey_result_id(survey_result_text=survey_result)
        builder.button(
            text=survey_result,
            callback_data=SelectSurveyResultCallbackFactory(
                action=ListSelectSurveyResultActions.RESULT_SELECTION,
                survey_result_id=survey_result_id
            )
        )

    builder.adjust(1, repeat=True)

    navigate_buttons = []
    if page_status not in [PAGING_STATUS.FIRST_PAGE, PAGING_STATUS.ONLY_PAGE, PAGING_STATUS.NO_PAGE]:
        previous_button = InlineKeyboardButton(
            text="Назад",
            callback_data=SelectSurveyResultCallbackFactory(action=ListSelectSurveyResultActions.PREVIOUS_RESULTS).pack())
        navigate_buttons.append(previous_button)
    if page_status not in [PAGING_STATUS.LAST_PAGE, PAGING_STATUS.ONLY_PAGE, PAGING_STATUS.NO_PAGE]:
        next_button = InlineKeyboardButton(
            text="Вперед",
            callback_data=SelectSurveyResultCallbackFactory(action=ListSelectSurveyResultActions.NEXT_RESULTS).pack())
        navigate_buttons.append(next_button)
    builder.row(*navigate_buttons)

    return_to_survey_actions_button = InlineKeyboardButton(
        text="Вернуться к действиям с опросом",
        callback_data=SelectSurveyResultCallbackFactory(action=ListSelectSurveyResultActions.RETURN_TO_SURVEY_ACTIONS).pack()
    )
    builder.row(return_to_survey_actions_button)
    return builder

def get_keyboard_for_survey_result_actions() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    see_answers_button = InlineKeyboardButton(
        text="Посмотреть свои ответы",
        callback_data=SurveyResultActionsCallbackFactory(action=ListSurveyResultActionsActions.SEE_ANSWERS).pack()
    )
    builder.row(see_answers_button)

    add_comments_button = InlineKeyboardButton(
        text="Добавить комментарии",
        callback_data=SurveyResultActionsCallbackFactory(action=ListSurveyResultActionsActions.ADD_COMMENTS).pack()
    )
    builder.row(add_comments_button)

    add_files_button = InlineKeyboardButton(
        text="Добавить файлы",
        callback_data=SurveyResultActionsCallbackFactory(action=ListSurveyResultActionsActions.ADD_FILES).pack()
    )
    builder.row(add_files_button)

    delete_result_button = InlineKeyboardButton(
        text="Удалить результат",
        callback_data=SurveyResultActionsCallbackFactory(action=ListSurveyResultActionsActions.DELETE_RESULT).pack()
    )
    builder.row(delete_result_button)
    
    return_button = InlineKeyboardButton(
        text="Вернуться к выбору результата",
        callback_data=SurveyResultActionsCallbackFactory(action=ListSurveyResultActionsActions.RETURN_TO_SELECT_SURVEY_RESULT).pack()
    )
    builder.row(return_button)
    
    return builder

def get_keyboard_for_confirm_delete_survey_result() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    
    confirm_delete_button = InlineKeyboardButton(
        text="Удалить результат",
        callback_data=SurveyResultActionsCallbackFactory(action=ListSurveyResultActionsActions.CONFIRM_DELETE_RESULT).pack()
    )
    builder.row(confirm_delete_button)
    
    return_button = InlineKeyboardButton(
        text="Вернуться",
        callback_data=SurveyResultActionsCallbackFactory(action=ListSurveyResultActionsActions.REJECT_DELETE_RESULT).pack()
    )
    builder.row(return_button)
    
    return builder

def get_keyboard_for_add_comments() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    
    return_button = InlineKeyboardButton(
        text="Преждевременно завершить добавление комментариев",
        callback_data=AddCommentsCallbackFactory(action=ListAddCommentsActions.RETURN_TO_SURVEY_RESULT_ACTIONS).pack()
    )
    builder.row(return_button)

    return builder

def get_keyboard_for_add_files() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    
    return_button = InlineKeyboardButton(
        text="Преждевременно завершить добавление файлов",
        callback_data=AddFilesCallbackFactory(action=ListAddFilesActions.RETURN_TO_SURVEY_RESULT_ACTIONS).pack()
    )
    builder.row(return_button)
    
    reply_builder = ReplyKeyboardBuilder()
    reply_builder.row(KeyboardButton(text="✅готово"))
    reply_kb = reply_builder.as_markup(resize_keyboard=True)

    return builder, reply_kb

def get_keyboard_for_send_survey_result_to_admin(link: str) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    link_button = InlineKeyboardButton(
        text="Ссылка на результат",
        url=link
    )
    builder.row(link_button)

    return builder

def get_keyboard_for_unprocessed_survey_results(survey_results: list, page_status: PAGING_STATUS) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    
    navigate_buttons = []
    if page_status not in [PAGING_STATUS.FIRST_PAGE, PAGING_STATUS.ONLY_PAGE, PAGING_STATUS.NO_PAGE]:
        previous_button = InlineKeyboardButton(
            text="Назад",
            callback_data=UnprocessedSurveyResultsCallbackFactory(action=ListUnprocessedSurveyResultsActions.PREVIOUS_RESULTS).pack())
        navigate_buttons.append(previous_button)
    if page_status not in [PAGING_STATUS.LAST_PAGE, PAGING_STATUS.ONLY_PAGE, PAGING_STATUS.NO_PAGE]:
        next_button = InlineKeyboardButton(
            text="Вперед",
            callback_data=UnprocessedSurveyResultsCallbackFactory(action=ListUnprocessedSurveyResultsActions.NEXT_RESULTS).pack())
        navigate_buttons.append(next_button)
    builder.row(*navigate_buttons)

    for survey_result in survey_results:
        button_text = f"{survey_result['telegram_id']}"
        builder.button(
            text=button_text,
            callback_data=UnprocessedSurveyResultsCallbackFactory(
                action=ListUnprocessedSurveyResultsActions.RESULT_SELECTION,
                survey_result_id=survey_result["survey_result_id"]
            )
        )

    builder.adjust(1, repeat=True)

    return_to_main_menu_button = InlineKeyboardButton(
        text="Вернуться в главное меню",
        callback_data=UnprocessedSurveyResultsCallbackFactory(action=ListUnprocessedSurveyResultsActions.RETURN_TO_MAIN_MENU).pack()
    )
    builder.row(return_to_main_menu_button)
    return builder

def get_keyboard_for_unprocessed_survey_result_actions(link: str) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    
    link_button = InlineKeyboardButton(
        text="Открыть результат",
        url=link
    )
    builder.row(link_button)
    
    mark_processed_button = InlineKeyboardButton(
        text="Пометить как обработанный",
        callback_data=UnprocessedSurveyResultCallbackFactory(action=ListUnprocessedSurveyResultActions.MARK_AS_PROCESSED).pack()
    )
    builder.row(mark_processed_button)
    
    return_button = InlineKeyboardButton(
        text="Вернуться к списку",
        callback_data=UnprocessedSurveyResultCallbackFactory(action=ListUnprocessedSurveyResultActions.RETURN_TO_UNPROCESSED_RESULTS).pack()
    )
    builder.row(return_button)
    
    return builder

def get_keyboard_for_confirm_mark_as_processed() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    
    confirm_button = InlineKeyboardButton(
        text="Да, пометить как обработанный",
        callback_data=UnprocessedSurveyResultCallbackFactory(action=ListUnprocessedSurveyResultActions.CONFIRM_MARK_AS_PROCESSED).pack()
    )
    builder.row(confirm_button)
    
    reject_button = InlineKeyboardButton(
        text="Отмена",
        callback_data=UnprocessedSurveyResultCallbackFactory(action=ListUnprocessedSurveyResultActions.REJECT_MARK_AS_PROCESSED).pack()
    )
    builder.row(reject_button)
    
    return builder
