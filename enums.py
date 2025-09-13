from enum import Enum


class RedisTmpFields(Enum):
    ENTER_NEW_ADMIN_TG_ID_REQUEST_MESSAGE_ID = "enter_new_admin_tg_id_request_message_id"
    ENTER_NEW_ADMIN_TG_ID_REQUEST_CHAT_ID = "enter_new_admin_tg_id_request_chat_id"
    ENTER_NEW_SURVEY_NAME_REQUEST_MESSAGE_ID = "enter_new_survey_name_request_message_id"
    ENTER_NEW_SURVEY_NAME_REQUEST_CHAT_ID = "enter_new_survey_name_request_chat_id"
    ENTER_NEW_SURVEY_STEP_FIELD_VALUE_REQUEST_MESSAGE_ID = "enter_new_survey_step_field_value_request_message_id"
    ENTER_NEW_SURVEY_STEP_FIELD_VALUE_REQUEST_CHAT_ID = "enter_new_survey_step_field_value_request_chat_id"
    ENTER_SURVEY_STEP_FIELD_VALUE_REQUEST_MESSAGE_ID = "enter_survey_step_field_value_request_message_id"
    ENTER_SURVEY_STEP_FIELD_VALUE_REQUEST_CHAT_ID = "enter_survey_step_field_value_request_chat_id"
    ENTER_NEW_SURVEY_FIELD_VALUE_REQUEST_MESSAGE_ID = "enter_new_survey_field_value_request_message_id"
    ENTER_NEW_SURVEY_FIELD_VALUE_REQUEST_CHAT_ID = "enter_new_survey_field_value_request_chat_id"

    DUMP_EDIT_SURVEYS = "dump_edit_surveys"
    DUMP_EDIT_SURVEY = "dump_edit_survey"
    DUMP_SET_STEPS_ORDER = "dump_set_steps_order"
    DUMP_CLINICAL_CASES_SURVEY_STEPS = "dump_clinical_cases_survey_steps"
    DUMP_SELECT_TAKE_SURVEY = "dump_select_take_survey"
    DUMP_TAKE_SURVEY = "dump_take_survey"

    EDIT_SURVEYS_IDX_MAP = "edit_surveys_idx_map"
    EDIT_SURVEY_LIST_STEPS = "edit_survey_list_steps"
    EDIT_SURVEY_SURVEY_ID = "edit_survey_survey_id"
    EDIT_SURVEY_STEPS_SURVEY_ID = "edit_survey_steps_survey_id"
    EDIT_SURVEY_STEPS_STEP_ID = "edit_survey_steps_step_id"
    EDIT_SURVEY_STEPS_CURRENT_FIELD_ID = "edit_survey_steps_current_field"
    CHANGE_SURVEY_STEPS_SURVEY_ID = "change_survey_steps_survey_id"
    CHANGE_SURVEY_STEPS_STEP_ID = "change_survey_steps_step_id"
    CHANGE_SURVEY_STEPS_CURRENT_FIELD_ID = "change_survey_steps_current_field"
    CHANGE_SURVEY_SURVEY_ID = "change_survey_survey_id"
    CHANGE_SURVEY_CURRENT_FIELD_ID = "change_survey_current_field"
    SET_STEPS_ORDER_SURVEY_ID = "set_steps_order_survey_id"
    SET_STEPS_ORDER_LIST_STEPS = "set_steps_order_list_steps"
    ADD_SURVEY_STEP_SURVEY_ID = "add_survey_step_survey_id"
    ADD_SURVEY_STEP_CURRENT_FIELD_ID = "add_survey_step_current_field"
    ADD_SURVEY_STEP_TEMPLATE_ADDED_STEP = "add_survey_step_template_added_step"
    ADD_SURVEY_CURRENT_FIELD_ID = "add_survey_current_field"
    ADD_SURVEY_TEMPLATE_ADDED_SURVEY = "add_survey_template_added_survey"
    SELECT_TAKE_SURVEY_IDX_MAP = "select_take_survey_idx_map"
    TAKE_SURVEY_SURVEY_ANSWER = "take_survey_survey_answer"
    TAKE_SURVEY_SURVEY_ID = "take_survey_survey_id"
    SEND_MESSAGE_TO_USER_FROM_USER_ID = "send_message_to_user_from_user_id"
    SEND_MESSAGE_TO_USER_REPLY_MESSAGE_ID = "send_message_to_user_reply_message_id"

class USER_TYPE(Enum):
    ADMIN = "admin"
    CLIENT = "client"

class SURVEY_STEP_TYPE(Enum):
    STRING = "string"
    FILES = "files"

class SURVEY_STEP_VARIABLE_FILEDS(Enum):
    NAME = "name"
    TEXT = "text"
    TYPE = "type"

class SURVEY_VARIABLE_FIELDS(Enum):
    NAME = "name"
    START_MESSAGE = "start_message"
    FINISH_MESSAGE = "finish_message"

class ListUserMainMenuActions(Enum):
    TAKE_THE_SURVEY = "take_the_survey"
    SEND_MESSAGE_TO_ADMIN = "send_message_to_admin"

class ListAdminMainMenuActions(Enum):
    TAKE_THE_SURVEY = "take_the_survey"
    EDIT_SURVEYS = "edit_surveys"
    EDIT_ADMIN_LIST = "edit_admin_list"
    GET_DUMP_USERS = "get_dump_users"

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
    CHANGE_SURVEY = "change_survey"
    SET_STEPS_ORDER = "set_steps_order"
    DELETE_SURVEY = "delete_survey"
    CONFIRM_DELETE_SURVEY = "confirm_delete_survey"
    REJECT_DELETE_SURVEY = "reject_delete_survey"
    RETURN = "return"

class ListAddSurveyListActions(Enum):
    RETURN_TO_EDIT_SURVEYS = "return_to_edit_surveys"

class ListEditSurveyStepsActions(Enum):
    CHANGE_STEP = "change_step"
    DELETE_STEP = "delete_step"
    CONFIRM_DELETE_STEP = "confirm_delete_step"
    REJECT_DELETE_STEP = "reject_delete_step"
    RETURN_TO_EDIT_SURVEY = "return_to_edit_survey"

class ListChangeSurveyStepsActions(Enum):
    KEEP_CURRENT_VALUE = "keep_current_value"
    SELECT_STEP_TYPE = "select_step_type"

class ListChangeSurveyActions(Enum):
    KEEP_CURRENT_VALUE = "keep_current_value"

class ListSetStepsOrderActions(Enum):
    NEXT_STEPS = "next_steps"
    PREVIOUS_STEPS = "previous_steps"
    KEEP_CURRENT_VALUE = "keep_current_value"

class ListAddSurveyStepActions(Enum):
    SELECT_STEP_TYPE = "select_step_type"

class ListSelectTakeSurveyActions(Enum):
    TAKE_SELECTION = "take_selection"
    NEXT_SURVEYS = "next_surveys"
    PREVIOUS_SURVEYS = "previous_surveys"
    RETURN_TO_MAIN_MENU = "return_to_main_menu"

class ListTakeSurveyActions(Enum):
    RETURN_TO_SELECT_TAKE_SURVEY = "return_to_select_take_survey"
    START_SURVEY = "start_survey"

class ListSendMessageToAdminActions(Enum):
    RETURN_TO_MAIN_MENU = "return_to_main_menu"

class ListReplyMessageToClientActions(Enum):
    REPLY_TO_CLIENT = "reply_to_client"

class ListSendMessageToUserActions(Enum):
    RETURN_TO_MAIN_MENU = "return_to_main_menu"
