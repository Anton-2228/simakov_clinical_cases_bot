from typing import TYPE_CHECKING, Dict

from aiogram_wrapper import AiogramWrapper
from commands.base_command import BaseCommand
from commands.manager import Manager
from commands.start import Start
from db.service.abc_services import ABCServices

from .add_survey import AddSurvey
from .add_survey_step import AddSurveyStep
from .add_user_to_admin_list import AddUserToAdminLit
from .admin_main_menu import AdminMainMenu
from .change_survey import ChangeSurvey
from .change_survey_step import ChangeSurveyStep
from .delete_user_from_admin_list import DeleteUserFromAdminLit
from .edit_admin_list import EditAdminList
from .edit_survey import EditSurvey
from .edit_survey_step import EditSurveyStep
from .edit_surveys import EditSurveys
from .registration import Registration
from .reply_to_client import ReplyMessageToClient
from .select_survey_result import SelectSurveyResult
from .select_take_survey import SelectTakeSurvey
from .select_user_to_send_message import SelectUserToSendMessage
from .send_message_to_admin import SendMessageToAdmin
from .send_message_to_user import SendMessageToUser
from .set_steps_order import SetStepsOrder
from .survey_actions import SurveyActions
from .survey_result_actions import SurveyResultActions
from .take_survey import TakeSurvey
from .user_main_menu import UserMainMenu

if TYPE_CHECKING:
    from .manager import Manager

def get_user_commands(manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> Dict[str, BaseCommand]:
    commands = {
        "start": Start(manager, db, aiogram_wrapper),
        "registration": Registration(manager, db, aiogram_wrapper),
        "main_menu": UserMainMenu(manager, db, aiogram_wrapper),
        "select_take_survey": SelectTakeSurvey(manager, db, aiogram_wrapper),
        "take_survey": TakeSurvey(manager, db, aiogram_wrapper),
        "send_message_to_admin": SendMessageToAdmin(manager, db, aiogram_wrapper),
        "survey_actions": SurveyActions(manager, db, aiogram_wrapper),
        "select_survey_result": SelectSurveyResult(manager, db, aiogram_wrapper),
        "survey_result_actions": SurveyResultActions(manager, db, aiogram_wrapper)
    }
    return commands

def get_admin_commands(manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> Dict[str, BaseCommand]:
    commands = {
        "start": Start(manager, db, aiogram_wrapper),
        "main_menu": AdminMainMenu(manager, db, aiogram_wrapper),
        "select_take_survey": SelectTakeSurvey(manager, db, aiogram_wrapper),
        "edit_admin_list": EditAdminList(manager, db, aiogram_wrapper),
        "add_user_to_admin_list": AddUserToAdminLit(manager, db, aiogram_wrapper),
        "delete_user_from_admin_list": DeleteUserFromAdminLit(manager, db, aiogram_wrapper),
        "edit_surveys": EditSurveys(manager, db, aiogram_wrapper),
        "add_survey": AddSurvey(manager, db, aiogram_wrapper),
        "edit_survey": EditSurvey(manager, db, aiogram_wrapper),
        "change_survey": ChangeSurvey(manager, db, aiogram_wrapper),
        "edit_survey_step": EditSurveyStep(manager, db, aiogram_wrapper),
        "change_survey_step": ChangeSurveyStep(manager, db, aiogram_wrapper),
        "add_survey_step": AddSurveyStep(manager, db, aiogram_wrapper),
        "set_steps_order": SetStepsOrder(manager, db, aiogram_wrapper),
        "take_survey": TakeSurvey(manager, db, aiogram_wrapper),
        "send_message_to_user": SendMessageToUser(manager, db, aiogram_wrapper),
        "reply_message_to_client": ReplyMessageToClient(manager, db, aiogram_wrapper),
        "select_user_to_send_message": SelectUserToSendMessage(manager, db, aiogram_wrapper),
        "survey_actions": SurveyActions(manager, db, aiogram_wrapper),
        "select_survey_result": SelectSurveyResult(manager, db, aiogram_wrapper),
        "survey_result_actions": SurveyResultActions(manager, db, aiogram_wrapper)
    }
    return commands
