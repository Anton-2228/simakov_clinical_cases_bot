import logging
from typing import Optional, TYPE_CHECKING

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import EditAdminListCallbackFactory, EditClinicalCasesSurveyCallbackFactory
from commands import BaseCommand
from db.service.services import Services
from enums import ListEditAdminListActions, USER_TYPE, ListEditClinicalCasesSurveyActions
from keyboards_generators import get_keyboard_for_edit_admin_list
from output_generators import create_edit_admin_list_output
from resources.messages import REQUEST_ENTER_NEW_ADMIN_MESSAGE
from states import States

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from commands import Manager

class EditClinicalCasesSurvey(BaseCommand):
    def __init__(self, manager: "Manager", db: Services, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_callback(self._edit_selection, EditClinicalCasesSurveyCallbackFactory.filter(F.action == ListEditClinicalCasesSurveyActions.EDIT_SELECTION))
        self.aiogram_wrapper.register_callback(self._next_steps, EditClinicalCasesSurveyCallbackFactory.filter(F.action == ListEditClinicalCasesSurveyActions.NEXT_STEPS))
        self.aiogram_wrapper.register_callback(self._previous_steps, EditClinicalCasesSurveyCallbackFactory.filter(F.action == ListEditClinicalCasesSurveyActions.PREVIOUS_STEPS))
        self.aiogram_wrapper.register_callback(self._add_new_step, EditClinicalCasesSurveyCallbackFactory.filter(F.action == ListEditClinicalCasesSurveyActions.ADD_NEW_STEP))
        self.aiogram_wrapper.register_callback(self._set_steps_order, EditClinicalCasesSurveyCallbackFactory.filter(F.action == ListEditClinicalCasesSurveyActions.SET_STEPS_ORDER))
        self.aiogram_wrapper.register_callback(self._return_to_main_menu, EditClinicalCasesSurveyCallbackFactory.filter(F.action == ListEditClinicalCasesSurveyActions.RETURN_TO_MAIN_MENU))

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None):
        pass

    async def _edit_selection(self, callback: CallbackQuery, callback_data: EditClinicalCasesSurveyCallbackFactory, state: FSMContext):
        pass

    async def _next_steps(self, callback: CallbackQuery, callback_data: EditClinicalCasesSurveyCallbackFactory, state: FSMContext):
        pass

    async def _previous_steps(self, callback: CallbackQuery, callback_data: EditClinicalCasesSurveyCallbackFactory, state: FSMContext):
        pass

    async def _add_new_step(self, callback: CallbackQuery, callback_data: EditClinicalCasesSurveyCallbackFactory, state: FSMContext):
        pass

    async def _set_steps_order(self, callback: CallbackQuery, callback_data: EditClinicalCasesSurveyCallbackFactory, state: FSMContext):
        pass

    async def _return_to_main_menu(self, callback: CallbackQuery, callback_data: EditClinicalCasesSurveyCallbackFactory, state: FSMContext):
        pass