from typing import TYPE_CHECKING, Dict

from aiogram_wrapper import AiogramWrapper
from commands.base_command import BaseCommand
from commands.manager import Manager
from commands.start import Start
from db.service.abc_services import ABCServices
from .add_comments_to_survey_result import AddCommentsToSurveyResult
from .add_files_to_survey_result import AddFilesToSurveyResult
from .unprocessed_survey_results import UnprocessedSurveyResults
from .unprocessed_survey_result_actions import UnprocessedSurveyResultActions

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
from .send_message_to_all_users import SendMessageToAllUsers
from .set_steps_order import SetStepsOrder
from .survey_actions import SurveyActions
from .survey_result_actions import SurveyResultActions
from .take_survey import TakeSurvey
from .user_main_menu import UserMainMenu

if TYPE_CHECKING:
    from .manager import Manager

def get_all_commands(manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> Dict[str, BaseCommand]:
    commands = {
        "start": Start(manager, db, aiogram_wrapper),
        "registration": Registration(manager, db, aiogram_wrapper),
        "user_main_menu": UserMainMenu(manager, db, aiogram_wrapper),
        "admin_main_menu": AdminMainMenu(manager, db, aiogram_wrapper),
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
        "send_message_to_admin": SendMessageToAdmin(manager, db, aiogram_wrapper),
        "send_message_to_all_users": SendMessageToAllUsers(manager, db, aiogram_wrapper),
        "reply_message_to_client": ReplyMessageToClient(manager, db, aiogram_wrapper),
        "select_user_to_send_message": SelectUserToSendMessage(manager, db, aiogram_wrapper),
        "survey_actions": SurveyActions(manager, db, aiogram_wrapper),
        "select_survey_result": SelectSurveyResult(manager, db, aiogram_wrapper),
        "survey_result_actions": SurveyResultActions(manager, db, aiogram_wrapper),
        "add_comments_to_survey_result": AddCommentsToSurveyResult(manager, db, aiogram_wrapper),
        "add_files_to_survey_result": AddFilesToSurveyResult(manager, db, aiogram_wrapper),
        "unprocessed_survey_results": UnprocessedSurveyResults(manager, db, aiogram_wrapper),
        "unprocessed_survey_result_actions": UnprocessedSurveyResultActions(manager, db, aiogram_wrapper)
    }
    return commands

def get_user_commands(all_commands: Dict[str, BaseCommand]) -> Dict[str, BaseCommand]:
    commands = {
        "start": all_commands["start"],
        "registration": all_commands["registration"],
        "main_menu": all_commands["user_main_menu"],
        "select_take_survey": all_commands["select_take_survey"],
        "take_survey": all_commands["take_survey"],
        "send_message_to_admin": all_commands["send_message_to_admin"],
        "survey_actions": all_commands["survey_actions"],
        "select_survey_result": all_commands["select_survey_result"],
        "survey_result_actions": all_commands["survey_result_actions"],
        "add_comments_to_survey_result": all_commands["add_comments_to_survey_result"],
        "add_files_to_survey_result": all_commands["add_files_to_survey_result"],
    }
    return commands

def get_admin_commands(all_commands: Dict[str, BaseCommand]) -> Dict[str, BaseCommand]:
    commands = {
        "start": all_commands["start"],
        "main_menu": all_commands["admin_main_menu"],
        "select_take_survey": all_commands["select_take_survey"],
        "edit_admin_list": all_commands["edit_admin_list"],
        "add_user_to_admin_list": all_commands["add_user_to_admin_list"],
        "delete_user_from_admin_list": all_commands["delete_user_from_admin_list"],
        "edit_surveys": all_commands["edit_surveys"],
        "add_survey": all_commands["add_survey"],
        "edit_survey": all_commands["edit_survey"],
        "change_survey": all_commands["change_survey"],
        "edit_survey_step": all_commands["edit_survey_step"],
        "change_survey_step": all_commands["change_survey_step"],
        "add_survey_step": all_commands["add_survey_step"],
        "set_steps_order": all_commands["set_steps_order"],
        "take_survey": all_commands["take_survey"],
        "send_message_to_user": all_commands["send_message_to_user"],
        "send_message_to_all_users": all_commands["send_message_to_all_users"],
        "reply_message_to_client": all_commands["reply_message_to_client"],
        "select_user_to_send_message": all_commands["select_user_to_send_message"],
        "survey_actions": all_commands["survey_actions"],
        "select_survey_result": all_commands["select_survey_result"],
        "survey_result_actions": all_commands["survey_result_actions"],
        "add_comments_to_survey_result": all_commands["add_comments_to_survey_result"],
        "add_files_to_survey_result": all_commands["add_files_to_survey_result"],
        "unprocessed_survey_results": all_commands["unprocessed_survey_results"],
        "unprocessed_survey_result_actions": all_commands["unprocessed_survey_result_actions"],
    }
    return commands
