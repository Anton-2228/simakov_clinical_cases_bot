from typing import Optional

from aiogram.filters.callback_data import CallbackData

from enums import (SURVEY_STEP_TYPE, SURVEY_STEP_VARIABLE_FILEDS, SURVEY_VARIABLE_FIELDS,
                   ListAddSurveyListActions, ListAddSurveyStepActions,
                   ListAddUserToAdminListActions, ListAdminMainMenuActions,
                   ListChangeSurveyActions, ListChangeSurveyStepsActions,
                   ListDeleteUserFromAdminListActions,
                   ListEditAdminListActions, ListEditSurveyActions,
                   ListEditSurveysActions, ListEditSurveyStepsActions,
                   ListSelectTakeSurveyActions, ListSetStepsOrderActions,
                   ListTakeSurveyActions, ListUserMainMenuActions, ListSendMessageToAdminActions,
                   ListSendMessageToUserActions, ListSendMessageToAllUsersActions, ListReplyMessageToClientActions,
                   ListSelectUserToSendMessageActions, ListSurveyActionsActions,
                   ListSelectSurveyResultActions, ListSurveyResultActionsActions,
                   ListAddCommentsActions, ListAddFilesActions, YES_NO)


class UserMainMenuCallbackFactory(CallbackData, prefix="umm"): # user_main_menu
    action: ListUserMainMenuActions

class AdminMainMenuCallbackFactory(CallbackData, prefix="amm"): # admin_main_menu
    action: ListAdminMainMenuActions

class EditAdminListCallbackFactory(CallbackData, prefix="eal"): # edit_admin_list
    action: ListEditAdminListActions

class AddUserToAdminListCallbackFactory(CallbackData, prefix="autal"): # add_user_to_admin_list
    action: ListAddUserToAdminListActions

class DeleteUserFromAdminListCallbackFactory(CallbackData, prefix="dufal"): # delete_user_from_admin_list
    action: ListDeleteUserFromAdminListActions
    user_id: Optional[int] = None

class EditSurveysCallbackFactory(CallbackData, prefix="ess"): # edit_surveyS
    action: ListEditSurveysActions
    survey_id: Optional[int] = None

class EditSurveyCallbackFactory(CallbackData, prefix="es"): # edit_survey
    action: ListEditSurveyActions
    step_id: Optional[int] = None

class AddSurveyCallbackFactory(CallbackData, prefix="as"): # add_survey
    action: ListAddSurveyListActions

class EditSurveyStepsCallbackFactory(CallbackData, prefix="esst"): # edit_survey_steps
    action: ListEditSurveyStepsActions

class ChangeSurveyStepsCallbackFactory(CallbackData, prefix="csst"): # change_survey_steps
    action: ListChangeSurveyStepsActions
    step_type: Optional[SURVEY_STEP_TYPE] = None

class ChangeSurveyCallbackFactory(CallbackData, prefix="cs"): # change_survey
    action: ListChangeSurveyActions

class SetStepsOrderCallbackFactory(CallbackData, prefix="sso"): # set_steps_order
    action: ListSetStepsOrderActions

class AddSurveyStepCallbackFactory(CallbackData, prefix="ass"): # add_survey_step
    action: ListAddSurveyStepActions
    step_type: Optional[SURVEY_STEP_TYPE] = None

class SelectTakeSurveyCallbackFactory(CallbackData, prefix="sts"): # select_take_survey
    action: ListSelectTakeSurveyActions
    survey_id: Optional[int] = None

class TakeSurveyCallbackFactory(CallbackData, prefix="ts"): # take_survey
    action: ListTakeSurveyActions
    yes_no_result: Optional[YES_NO] = None

class SendMessageToAdminCallbackFactory(CallbackData, prefix="smta"): # send_message_to_admin
    action: ListSendMessageToAdminActions

class ReplyMessageToClientCallbackFactory(CallbackData, prefix="rmtc"): # reply_message_to_client
    action: ListReplyMessageToClientActions
    from_user_id: int

class SendMessageToUserCallbackFactory(CallbackData, prefix="smtu"): # send_message_to_user
    action: ListSendMessageToUserActions

class SendMessageToAllUsersCallbackFactory(CallbackData, prefix="smta"): # send_message_to_all_users
    action: ListSendMessageToAllUsersActions

class SelectUserToSendMessageCallbackFactory(CallbackData, prefix="sutsm"): # select_user_to_send_message
    action: ListSelectUserToSendMessageActions
    user_id: Optional[int] = None

class SurveyActionsCallbackFactory(CallbackData, prefix="sa"): # survey_actions
    action: ListSurveyActionsActions

class SelectSurveyResultCallbackFactory(CallbackData, prefix="ssr"): # select_survey_result
    action: ListSelectSurveyResultActions
    survey_result_id: Optional[int] = None

class SurveyResultActionsCallbackFactory(CallbackData, prefix="sra"): # survey_result_actions
    action: ListSurveyResultActionsActions

class AddCommentsCallbackFactory(CallbackData, prefix="ac"): # add_comments
    action: ListAddCommentsActions

class AddFilesCallbackFactory(CallbackData, prefix="af"): # add_files
    action: ListAddFilesActions
