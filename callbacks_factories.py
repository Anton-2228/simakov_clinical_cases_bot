from typing import Optional

from aiogram.filters.callback_data import CallbackData

from enums import ListUserMainMenuActions, ListAdminMainMenuActions, ListEditAdminListActions, \
    ListDeleteUserFromAdminListActions, ListAddUserToAdminListActions, ListEditSurveyActions, ListEditSurveysActions, \
    ListAddSurveyListActions, SURVEY_STEP_VARIABLE_FILEDS, ListEditSurveyStepsActions, SURVEY_STEP_TYPE, \
    ListSetStepsOrderActions


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
    step_type: Optional[SURVEY_STEP_TYPE] = None

class SetStepsOrderCallbackFactory(CallbackData, prefix="sso"): # set_steps_order
    action: ListSetStepsOrderActions
