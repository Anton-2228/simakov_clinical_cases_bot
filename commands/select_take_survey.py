import logging
from typing import TYPE_CHECKING, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import SelectTakeSurveyCallbackFactory
from db.service.abc_services import ABCServices
from enums import (ListSelectTakeSurveyActions, RedisTmpFields)
from keyboards_generators import get_keyboard_for_select_take_survey
from pagers.aiogram_pager import AiogramPager
from resources.messages import SELECT_TAKE_SURVEY
from states import States

from .base_command import BaseCommand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .manager import Manager

class SelectTakeSurvey(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_callback(self._take_selection, SelectTakeSurveyCallbackFactory.filter(F.action == ListSelectTakeSurveyActions.TAKE_SELECTION))
        self.aiogram_wrapper.register_callback(self._next_survey, SelectTakeSurveyCallbackFactory.filter(F.action == ListSelectTakeSurveyActions.NEXT_SURVEYS))
        self.aiogram_wrapper.register_callback(self._previous_survey, SelectTakeSurveyCallbackFactory.filter(F.action == ListSelectTakeSurveyActions.PREVIOUS_SURVEYS))
        self.aiogram_wrapper.register_callback(self._return_to_main_menu, SelectTakeSurveyCallbackFactory.filter(F.action == ListSelectTakeSurveyActions.RETURN_TO_MAIN_MENU))
        self.surveys_pager = AiogramPager(aiogram_wrapper=aiogram_wrapper,
                                          dump_field_name=RedisTmpFields.DUMP_SELECT_TAKE_SURVEY.value)

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None, **kwargs):
        surveys = await self.db.survey.get_all_surveys()
        surveys_names = []
        surveys_idx_map = {}
        for survey in surveys:
            surveys_names.append(survey.name)
            surveys_idx_map[survey.id] = survey.name
        await self.aiogram_wrapper.set_state_data(state_context=state, field_name=RedisTmpFields.SELECT_TAKE_SURVEY_IDX_MAP.value,
                                                  value=surveys_idx_map)
        await self.surveys_pager.init(state_context=state, elements=surveys_names, page_count=5)
        page_number, page_status, current_page = await self.surveys_pager.get_start_page(state_context=state)
        keyboard = get_keyboard_for_select_take_survey(surveys=current_page, survey_idx_map=surveys_idx_map, page_status=page_status)
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=SELECT_TAKE_SURVEY,
                                                                 reply_markup=keyboard.as_markup())

    async def _take_selection(self, callback: CallbackQuery, callback_data: SelectTakeSurveyCallbackFactory, state: FSMContext):
        survey_id = callback_data.survey_id
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.SELECT_TAKE_SURVEY)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="take_survey",
                                  message=callback.message,
                                  state=state,
                                  survey_id=survey_id)
        await callback.answer()

    async def _next_survey(self, callback: CallbackQuery, callback_data: SelectTakeSurveyCallbackFactory, state: FSMContext):
        surveys_idx_map = await self.aiogram_wrapper.get_state_data(state_context=state, field_name=RedisTmpFields.EDIT_SURVEYS_IDX_MAP.value)
        page_number, page_status, current_page = await self.surveys_pager.get_next_page(state_context=state)
        keyboard = get_keyboard_for_select_take_survey(surveys=current_page, survey_idx_map=surveys_idx_map, page_status=page_status)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        send_message = await self.manager.aiogram_wrapper.answer_massage(message=callback.message,
                                                                         text=SELECT_TAKE_SURVEY,
                                                                         reply_markup=keyboard.as_markup())
        await callback.answer()

    async def _previous_survey(self, callback: CallbackQuery, callback_data: SelectTakeSurveyCallbackFactory, state: FSMContext):
        surveys_idx_map = await self.aiogram_wrapper.get_state_data(state_context=state, field_name=RedisTmpFields.EDIT_SURVEYS_IDX_MAP.value)
        page_number, page_status, current_page = await self.surveys_pager.get_previous_page(state_context=state)
        keyboard = get_keyboard_for_select_take_survey(surveys=current_page, survey_idx_map=surveys_idx_map, page_status=page_status)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        send_message = await self.manager.aiogram_wrapper.answer_massage(message=callback.message,
                                                                         text=SELECT_TAKE_SURVEY,
                                                                         reply_markup=keyboard.as_markup())
        await callback.answer()

    async def _return_to_main_menu(self, callback: CallbackQuery, callback_data: SelectTakeSurveyCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.MAIN_MENU)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="main_menu",
                                  message=callback.message,
                                  state=state)
        await callback.answer()
