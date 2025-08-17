from typing import Dict, TYPE_CHECKING

from aiogram_wrapper import AiogramWrapper
from commands.base_command import BaseCommand
from commands.manager import Manager
from commands.start import Start

from db.service.abc_services import ABCServices
from .add_step import AddStep
from .add_survey import AddSurvey
from .add_user_to_admin_list import AddUserToAdminLit
from .admin_main_menu import AdminMainMenu
from .delete_user_from_admin_list import DeleteUserFromAdminLit
from .edit_admin_list import EditAdminList
from .edit_survey import EditSurvey
from .edit_survey_step import EditSurveyStep
from .edit_surveys import EditSurveys
from .registration import Registration
from .take_the_survey import TakeTheSurvey
from .user_main_menu import UserMainMenu
from .set_steps_order import SetStepsOrder

if TYPE_CHECKING:
    from .manager import Manager

def get_user_commands(manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> Dict[str, BaseCommand]:
    commands = {
        "start": Start(manager, db, aiogram_wrapper),
        "registration": Registration(manager, db, aiogram_wrapper),
        "main_menu": UserMainMenu(manager, db, aiogram_wrapper),
        "take_the_survey": TakeTheSurvey(manager, db, aiogram_wrapper)
    }
    return commands

def get_admin_commands(manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> Dict[str, BaseCommand]:
    commands = {
        "start": Start(manager, db, aiogram_wrapper),
        "main_menu": AdminMainMenu(manager, db, aiogram_wrapper),
        "take_the_survey": TakeTheSurvey(manager, db, aiogram_wrapper),
        "edit_admin_list": EditAdminList(manager, db, aiogram_wrapper),
        "add_user_to_admin_list": AddUserToAdminLit(manager, db, aiogram_wrapper),
        "delete_user_from_admin_list": DeleteUserFromAdminLit(manager, db, aiogram_wrapper),
        "edit_surveys": EditSurveys(manager, db, aiogram_wrapper),
        "add_survey": AddSurvey(manager, db, aiogram_wrapper),
        "edit_survey": EditSurvey(manager, db, aiogram_wrapper),
        "edit_survey_step": EditSurveyStep(manager, db, aiogram_wrapper),
        "add_step": AddStep(manager, db, aiogram_wrapper),
        "set_steps_order": SetStepsOrder(manager, db, aiogram_wrapper)
    }
    return commands
