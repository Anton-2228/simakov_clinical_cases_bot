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

class EditSurvey(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_callback(self._edit_selection, EditSurveyCallbackFactory.filter(F.action == ListEditSurveyActions.EDIT_SELECTION))
        self.aiogram_wrapper.register_callback(self._next_steps, EditSurveyCallbackFactory.filter(F.action == ListEditSurveyActions.NEXT_STEPS))
        self.aiogram_wrapper.register_callback(self._previous_steps, EditSurveyCallbackFactory.filter(F.action == ListEditSurveyActions.PREVIOUS_STEPS))
        self.aiogram_wrapper.register_callback(self._add_new_step, EditSurveyCallbackFactory.filter(F.action == ListEditSurveyActions.ADD_NEW_STEP))
        self.aiogram_wrapper.register_callback(self._set_steps_order, EditSurveyCallbackFactory.filter(F.action == ListEditSurveyActions.SET_STEPS_ORDER))
        self.aiogram_wrapper.register_callback(self._return, EditSurveyCallbackFactory.filter(F.action == ListEditSurveyActions.RETURN))
        self.products_pager = AiogramPager(aiogram_wrapper=aiogram_wrapper,
                                           dump_field_name=RedisTmpFields.DUMP_CLINICAL_CASES_SURVEY_STEPS.value)

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None):
        keyboard = get_keyboard_for_edit_survey()

    async def _edit_selection(self, callback: CallbackQuery, callback_data: EditSurveyCallbackFactory, state: FSMContext):
        pass

    async def _next_steps(self, callback: CallbackQuery, callback_data: EditSurveyCallbackFactory, state: FSMContext):
        pass

    async def _previous_steps(self, callback: CallbackQuery, callback_data: EditSurveyCallbackFactory, state: FSMContext):
        pass

    async def _add_new_step(self, callback: CallbackQuery, callback_data: EditSurveyCallbackFactory, state: FSMContext):
        pass

    async def _set_steps_order(self, callback: CallbackQuery, callback_data: EditSurveyCallbackFactory, state: FSMContext):
        pass

    async def _return(self, callback: CallbackQuery, callback_data: EditSurveyCallbackFactory, state: FSMContext):
        pass