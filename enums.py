from enum import Enum


class USER_TYPE(Enum):
    ADMIN = "admin"
    CLIENT = "client"

class SURVEY_STEP_TYPE(Enum):
    STRING = "string"
    FILES = "files"

class ListUserMainMenuActions(Enum):
    ADD_CLINICAL_CASE = "add_clinical_case"

class ListAdminMainMenuActions(Enum):
    ADD_CLINICAL_CASE = "add_clinical_case"
    EDIT_SURVEYS = "edit_surveys"
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

class ListEditSurveysActions(Enum):
    EDIT_SELECTION = "edit_selection"
    NEXT_SURVEYS = "next_surveys"
    PREVIOUS_SURVEYS = "previous_surveys"
    ADD_SURVEY = "add_survey"
    RETURN_TO_MAIN_MENU = "return_to_main_menu"

class ListEditSurveyActions(Enum):
    EDIT_SELECTION = "edit_selection"
    NEXT_STEPS = "next_steps"
    PREVIOUS_STEPS = "previous_steps"
    ADD_NEW_STEP = "add_new_step"
    SET_STEPS_ORDER = "set_steps_order"
    RETURN = "return"

class RedisTmpFields(Enum):
    ENTER_NEW_ADMIN_TG_ID_REQUEST_MESSAGE_ID = "enter_new_admin_tg_id_request_message_id"
    ENTER_NEW_ADMIN_TG_ID_REQUEST_CHAT_ID = "enter_new_admin_tg_id_request_chat_id"
    ENTER_NEW_SURVEY_NAME_REQUEST_MESSAGE_ID = "enter_new_survey_name_request_message_id"
    ENTER_NEW_SURVEY_NAME_REQUEST_CHAT_ID = "enter_new_survey_name_request_chat_id"

    DUMP_EDIT_SURVEYS = "dump_edit_surveys"
    DUMP_CLINICAL_CASES_SURVEY_STEPS = "dump_clinical_cases_survey_steps"

    EDIT_SURVEYS_LIST_SURVEYS = "edit_surveys_current_surveys"
    EDIT_SURVEYS_IDX_MAP = "edit_surveys_idx_map"

class ListAddSurveyListActions(Enum):
    RETURN_TO_EDIT_SURVEYS = "return_to_edit_surveys"
