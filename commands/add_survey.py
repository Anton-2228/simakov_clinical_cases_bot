import logging
from typing import Optional, TYPE_CHECKING

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import EditAdminListCallbackFactory, EditSurveyCallbackFactory
from commands import BaseCommand
from db.service.abc_services import ABCServices
from enums import ListEditAdminListActions, USER_TYPE, ListEditSurveyActions, RedisTmpFields
from keyboards_generators import get_keyboard_for_edit_admin_list, get_keyboard_for_edit_survey
from output_generators import create_edit_admin_list_output
from pagers.aiogram_pager import AiogramPager
from resources.messages import REQUEST_ENTER_NEW_ADMIN_MESSAGE
from states import States

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from commands import Manager

class AddSurvey(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None):
        pass
