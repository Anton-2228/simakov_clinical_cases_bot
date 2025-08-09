from typing import Dict, TYPE_CHECKING

from aiogram_wrapper import AiogramWrapper
from commands.base_command import BaseCommand
from commands.manager import Manager
from commands.start import Start

from db.service.services import Services

if TYPE_CHECKING:
    from .manager import Manager

def get_user_commands(manager: "Manager", db: Services, aiogram_wrapper: AiogramWrapper) -> Dict[str, BaseCommand]:
    commands = {
        "start": Start(manager, db, aiogram_wrapper),
        # "main_menu": MainMenu(manager, db, aiogram_wrapper),
    }
    return commands
