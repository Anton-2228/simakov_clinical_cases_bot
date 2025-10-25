import logging
from typing import TYPE_CHECKING, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import UnprocessedSurveyResultsCallbackFactory
from db.service.abc_services import ABCServices
from enums import ListUnprocessedSurveyResultsActions, RedisTmpFields
from keyboards_generators import get_keyboard_for_unprocessed_survey_results
from output_generators import create_unprocessed_survey_results_output
from pagers.aiogram_pager import AiogramPager
from states import States

from .base_command import BaseCommand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .manager import Manager

class UnprocessedSurveyResults(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_callback(self._result_selection, UnprocessedSurveyResultsCallbackFactory.filter(F.action == ListUnprocessedSurveyResultsActions.RESULT_SELECTION))
        self.aiogram_wrapper.register_callback(self._next_results, UnprocessedSurveyResultsCallbackFactory.filter(F.action == ListUnprocessedSurveyResultsActions.NEXT_RESULTS))
        self.aiogram_wrapper.register_callback(self._previous_results, UnprocessedSurveyResultsCallbackFactory.filter(F.action == ListUnprocessedSurveyResultsActions.PREVIOUS_RESULTS))
        self.aiogram_wrapper.register_callback(self._return_to_main_menu, UnprocessedSurveyResultsCallbackFactory.filter(F.action == ListUnprocessedSurveyResultsActions.RETURN_TO_MAIN_MENU))
        self.survey_results_pager = AiogramPager(aiogram_wrapper=aiogram_wrapper,
                                                   dump_field_name=RedisTmpFields.DUMP_UNPROCESSED_SURVEY_RESULTS.value)

    async def execute(self,
                      message: Message,
                      state: FSMContext,
                      command: Optional[CommandObject] = None,
                      **kwargs):
        survey_results = await self.db.survey_result.get_unprocessed_survey_results()
        
        survey_results_with_users = []
        
        for survey_result in survey_results:
            user = await self.db.user.get_user(telegram_id=survey_result.user_id)
            res = {"survey_result_id": survey_result.id,
                   "survey_name": survey_result.survey.name,
                   "full_name": user.full_name,
                   "telegram_id": user.telegram_id}
            survey_results_with_users.append(res)
        
        await self.survey_results_pager.init(state_context=state, elements=survey_results_with_users, page_count=5)
        page_number, page_status, current_page = await self.survey_results_pager.get_start_page(state_context=state)
        
        keyboard = get_keyboard_for_unprocessed_survey_results(survey_results=current_page,
                                                              page_status=page_status)
        
        text_message = create_unprocessed_survey_results_output(current_page)
        
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                               text=text_message,
                                                               reply_markup=keyboard.as_markup())

    async def _result_selection(self, callback: CallbackQuery, callback_data: UnprocessedSurveyResultsCallbackFactory, state: FSMContext):
        survey_result_id = callback_data.survey_result_id
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.UNPROCESSED_SURVEY_RESULT_ACTIONS)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="unprocessed_survey_result_actions",
                                  message=callback.message,
                                  state=state,
                                  survey_result_id=survey_result_id)
        await callback.answer()

    async def _next_results(self, callback: CallbackQuery, callback_data: UnprocessedSurveyResultsCallbackFactory, state: FSMContext):
        page_number, page_status, current_page = await self.survey_results_pager.get_next_page(state_context=state)
        
        keyboard = get_keyboard_for_unprocessed_survey_results(survey_results=current_page,
                                                              page_status=page_status)
        text_message = create_unprocessed_survey_results_output(current_page)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        send_message = await self.manager.aiogram_wrapper.answer_massage(message=callback.message,
                                                                         text=text_message,
                                                                         reply_markup=keyboard.as_markup())
        await callback.answer()

    async def _previous_results(self, callback: CallbackQuery, callback_data: UnprocessedSurveyResultsCallbackFactory, state: FSMContext):
        page_number, page_status, current_page = await self.survey_results_pager.get_previous_page(state_context=state)
        
        keyboard = get_keyboard_for_unprocessed_survey_results(survey_results=current_page,
                                                              page_status=page_status)
        text_message = create_unprocessed_survey_results_output(current_page)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        send_message = await self.manager.aiogram_wrapper.answer_massage(message=callback.message,
                                                                         text=text_message,
                                                                         reply_markup=keyboard.as_markup())
        await callback.answer()

    async def _return_to_main_menu(self, callback: CallbackQuery, callback_data: UnprocessedSurveyResultsCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.MAIN_MENU)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="main_menu",
                                  message=callback.message,
                                  state=state)
        await callback.answer()
