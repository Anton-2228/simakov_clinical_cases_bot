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
    TAKE_SURVEY_VALUE_REQUEST_MESSAGE_ID = "take_survey_value_request_message_id"
    TAKE_SURVEY_VALUE_REQUEST_CHAT_ID = "take_survey__value_request_chat_id"

    DUMP_EDIT_SURVEYS = "dump_edit_surveys"
    DUMP_EDIT_SURVEY = "dump_edit_survey"
    DUMP_SET_STEPS_ORDER = "dump_set_steps_order"
    DUMP_CLINICAL_CASES_SURVEY_STEPS = "dump_clinical_cases_survey_steps"
    DUMP_SELECT_TAKE_SURVEY = "dump_select_take_survey"
    DUMP_TAKE_SURVEY = "dump_take_survey"
    DUMP_SELECT_USER_TO_SEND_MESSAGE = "dump_select_user_to_send_message"
    DUMP_SELECT_SURVEY_RESULT = "dump_select_survey_result"
    DUMP_UNPROCESSED_SURVEY_RESULTS = "dump_unprocessed_survey_results"

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
    SURVEY_ACTIONS_SURVEY_ID = "survey_actions_survey_id"
    SEND_MESSAGE_TO_USER_FROM_USER_ID = "send_message_to_user_from_user_id"
    SEND_MESSAGE_TO_USER_REPLY_MESSAGE_ID = "send_message_to_user_reply_message_id"
    SELECT_USER_TO_SEND_MESSAGE_IDX_MAP = "select_user_to_send_message_idx_map"
    SELECT_SURVEY_RESULT_IDX_MAP = "select_survey_result_idx_map"
    SELECT_SURVEY_RESULT_SURVEY_ID = "select_survey_result_survey_id"
    SURVEY_RESULT_ACTIONS_SURVEY_RESULT_ID = "survey_result_actions_survey_result_id"
    ADD_COMMENTS_TO_SURVEY_RESULT_SURVEY_RESULT_ID = "add_comments_to_survey_result_survey_result_id"
    ADD_FILES_TO_SURVEY_RESULT_SURVEY_RESULT_ID = "add_files_to_survey_result_survey_result_id"
    ADD_FILES_TO_SURVEY_RESULT_ANSWER = "add_files_to_survey_result_answer"
    UNPROCESSED_SURVEY_RESULTS_IDX_MAP = "unprocessed_survey_results_idx_map"
    UNPROCESSED_SURVEY_RESULT_ACTIONS_SURVEY_RESULT_ID = "unprocessed_survey_result_actions_survey_result_id"

class USER_TYPE(Enum):
    ADMIN = "admin"
    CLIENT = "client"

class SURVEY_STEP_TYPE(Enum):
    STRING = "string"
    FILES = "files"
    YES_NO = "yes\\_no"

class YES_NO(Enum):
    YES = "yes"
    NO = "no"

class SURVEY_RESULT_COMMENT_TYPE(Enum):
    STRING = "string"
    FILES = "files"

class SURVEY_STEP_VARIABLE_FILEDS(Enum):
    NAME = "name"
    TEXT = "text"
    TYPE = "type"
    IMAGE = "image"

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
    SEND_MESSAGE_TO_USER = "send_message_to_user"
    UNPROCESSED_SURVEY_RESULTS = "unprocessed_survey_results"

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
    YES_NO_SELECTION = "yes_no_selection"

class ListSurveyActionsActions(Enum):
    TAKE_SURVEY = "take_survey"
    VIEW_COMPLETED_SURVEYS = "view_completed_surveys"
    RETURN_TO_MAIN_MENU = "return_to_main_menu"

class ListSendMessageToAdminActions(Enum):
    RETURN_TO_MAIN_MENU = "return_to_main_menu"

class ListReplyMessageToClientActions(Enum):
    REPLY_TO_CLIENT = "reply_to_client"

class ListSendMessageToUserActions(Enum):
    RETURN_TO_MAIN_MENU = "return_to_main_menu"

class ListSendMessageToAllUsersActions(Enum):
    RETURN_TO_MAIN_MENU = "return_to_main_menu"

class ListSelectUserToSendMessageActions(Enum):
    USER_SELECTION = "user_selection"
    NEXT_USERS = "next_users"
    PREVIOUS_USERS = "previous_users"
    SEND_TO_ALL_USERS = "send_to_all_users"
    RETURN_TO_MAIN_MENU = "return_to_main_menu"

class ListSelectSurveyResultActions(Enum):
    RESULT_SELECTION = "result_selection"
    NEXT_RESULTS = "next_results"
    PREVIOUS_RESULTS = "previous_results"
    RETURN_TO_SURVEY_ACTIONS = "return_to_survey_actions"

class ListSurveyResultActionsActions(Enum):
    DELETE_RESULT = "delete_result"
    CONFIRM_DELETE_RESULT = "confirm_delete_result"
    REJECT_DELETE_RESULT = "reject_delete_result"
    SEE_ANSWERS = "see_answers"
    ADD_COMMENTS = "add_comments"
    ADD_FILES = "add_files"
    RETURN_TO_SELECT_SURVEY_RESULT = "return_to_select_survey_result"

class ListAddCommentsActions(Enum):
    RETURN_TO_SURVEY_RESULT_ACTIONS = "return_to_survey_result_actions"

class ListAddFilesActions(Enum):
    RETURN_TO_SURVEY_RESULT_ACTIONS = "return_to_survey_result_actions"

class ListUnprocessedSurveyResultsActions(Enum):
    RESULT_SELECTION = "result_selection"
    NEXT_RESULTS = "next_results"
    PREVIOUS_RESULTS = "previous_results"
    RETURN_TO_MAIN_MENU = "return_to_main_menu"

class ListUnprocessedSurveyResultActions(Enum):
    OPEN_LINK = "open_link"
    MARK_AS_PROCESSED = "mark_as_processed"
    CONFIRM_MARK_AS_PROCESSED = "confirm_mark_as_processed"
    REJECT_MARK_AS_PROCESSED = "reject_mark_as_processed"
    RETURN_TO_UNPROCESSED_RESULTS = "return_to_unprocessed_results"
