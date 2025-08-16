from typing import Optional

from aiogram.filters.callback_data import CallbackData

from enums import ListUserMainMenuActions, ListAdminMainMenuActions, ListEditAdminListActions, \
    ListDeleteUserFromAdminListActions, ListAddUserToAdminListActions, ListEditSurveyActions, ListEditSurveysActions


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
