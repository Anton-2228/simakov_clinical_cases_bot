import logging
from typing import Optional, TYPE_CHECKING

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import UserMainMenuCallbackFactory

from db.service.services import Services
from enums import ListUserMainMenuActions
from keyboards_generators import get_keyboard_for_user_main_menu
from resources.messages import USER_MAIN_MENU_MESSAGE
from states import States
from .base_command import BaseCommand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .manager import Manager

class AddClinicalCase(BaseCommand):
    def __init__(self, manager: "Manager", db: Services, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None):
        pass
