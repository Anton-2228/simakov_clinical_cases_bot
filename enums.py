from enum import Enum


class USER_TYPE(Enum):
    ADMIN = "admin"
    CLIENT = "client"

class ListUserMainMenuActions(Enum):
    ADD_CLINICAL_CASE = "add_clinical_case"

class ListAdminMainMenuActions(Enum):
    ADD_CLINICAL_CASE = "add_clinical_case"
    EDIT_CLINICAL_CASES_SURVEY = "edit_clinical_cases_survey"
    EDIT_ADMIN_LIST = "edit_admin_list"

class ListEditAdminListActions(Enum):
    ADD_ADMIN = "add_admin"
    REMOVE_ADMIN = "remove_admin"
    RETURN_TO_MAIN_MENU = "return_to_main_menu"

class ListDeleteUserFromAdminListActions(Enum):
    DELETION_SELECTION = "deletion_selection"
    RETURN_TO_EDIT_ADMIN_LIST = "return_to_edit_admin_list"

class ListAddUserToAdminListActions(Enum):
    RETURN_TO_EDIT_ADMIN_LIST = "return_to_edit_admin_list"

class ListEditClinicalCasesSurveyActions(Enum):
    EDIT_SELECTION = "edit_selection"
    NEXT_STEPS = "next_steps"
    PREVIOUS_STEPS = "previous_steps"
    ADD_NEW_STEP = "add_new_step"
    SET_STEPS_ORDER = "set_steps_order"
    RETURN_TO_MAIN_MENU = "return_to_main_menu"

class RedisTmpFields(Enum):
    ENTER_NEW_ADMIN_TG_ID_REQUEST_MESSAGE_ID = "enter_new_admin_tg_id_request_message_id"
    ENTER_NEW_ADMIN_TG_ID_REQUEST_CHAT_ID = "enter_new_admin_tg_id_request_chat_id"
