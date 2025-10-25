import logging
from typing import TYPE_CHECKING, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import UnprocessedSurveyResultCallbackFactory
from db.postgres_models import SurveyResultStatus
from db.service.abc_services import ABCServices
from db.service.yandex_disk_wrapper import YANDEX_DISK_SESSION
from enums import ListUnprocessedSurveyResultActions, RedisTmpFields
from keyboards_generators import get_keyboard_for_unprocessed_survey_result_actions, get_keyboard_for_confirm_mark_as_processed
from output_generators import create_send_info_about_new_survey_result_output
from resources.messages import CONFIRM_MARK_AS_PROCESSED
from states import States

from .base_command import BaseCommand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .manager import Manager

class UnprocessedSurveyResultActions(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_callback(self._open_link, UnprocessedSurveyResultCallbackFactory.filter(F.action == ListUnprocessedSurveyResultActions.OPEN_LINK))
        self.aiogram_wrapper.register_callback(self._mark_as_processed, UnprocessedSurveyResultCallbackFactory.filter(F.action == ListUnprocessedSurveyResultActions.MARK_AS_PROCESSED))
        self.aiogram_wrapper.register_callback(self._confirm_mark_as_processed, UnprocessedSurveyResultCallbackFactory.filter(F.action == ListUnprocessedSurveyResultActions.CONFIRM_MARK_AS_PROCESSED))
        self.aiogram_wrapper.register_callback(self._reject_mark_as_processed, UnprocessedSurveyResultCallbackFactory.filter(F.action == ListUnprocessedSurveyResultActions.REJECT_MARK_AS_PROCESSED))
        self.aiogram_wrapper.register_callback(self._return_to_unprocessed_results, UnprocessedSurveyResultCallbackFactory.filter(F.action == ListUnprocessedSurveyResultActions.RETURN_TO_UNPROCESSED_RESULTS))

    async def execute(self,
                      message: Message,
                      state: FSMContext,
                      command: Optional[CommandObject] = None,
                      survey_result_id: Optional[int] = None,
                      **kwargs):
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.UNPROCESSED_SURVEY_RESULT_ACTIONS_SURVEY_RESULT_ID.value,
                                                  value=survey_result_id)
        survey_result = await self.db.survey_result.get_survey_result(id=survey_result_id)
        
        user = await self.db.user.get_user(telegram_id=survey_result.user_id)
        
        async with YANDEX_DISK_SESSION() as yd:
            link = await yd.get_folder_link(services=self.db, survey_result=survey_result)
        
        text = create_send_info_about_new_survey_result_output(user=user, survey_result=survey_result)
        keyboard = get_keyboard_for_unprocessed_survey_result_actions(link=link)
        
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=text,
                                                                 reply_markup=keyboard.as_markup())

    async def _open_link(self, callback: CallbackQuery, callback_data: UnprocessedSurveyResultCallbackFactory, state: FSMContext):
        await callback.answer()

    async def _mark_as_processed(self, callback: CallbackQuery, callback_data: UnprocessedSurveyResultCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        keyboard = get_keyboard_for_confirm_mark_as_processed()
        send_message = await self.aiogram_wrapper.answer_massage(message=callback.message,
                                                                 text=CONFIRM_MARK_AS_PROCESSED,
                                                                 reply_markup=keyboard.as_markup())
        await callback.answer()

    async def _confirm_mark_as_processed(self, callback: CallbackQuery, callback_data: UnprocessedSurveyResultCallbackFactory, state: FSMContext):
        survey_result_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                     field_name=RedisTmpFields.UNPROCESSED_SURVEY_RESULT_ACTIONS_SURVEY_RESULT_ID.value)
        
        survey_result = await self.db.survey_result.get_survey_result(id=survey_result_id)
        survey_result.status = SurveyResultStatus.PROCESSED
        await self.db.survey_result.update_survey_result(survey_result)
        
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.UNPROCESSED_SURVEY_RESULTS)
        await self.manager.launch(name="unprocessed_survey_results",
                                  message=callback.message,
                                  state=state)
        await callback.answer()

    async def _reject_mark_as_processed(self, callback: CallbackQuery, callback_data: UnprocessedSurveyResultCallbackFactory, state: FSMContext):
        survey_result_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                     field_name=RedisTmpFields.UNPROCESSED_SURVEY_RESULT_ACTIONS_SURVEY_RESULT_ID.value)
        
        survey_result = await self.db.survey_result.get_survey_result(id=survey_result_id)
        user = await self.db.user.get_user(telegram_id=survey_result.user_id)
        
        async with YANDEX_DISK_SESSION() as yd:
            link = await yd.get_folder_link(services=self.db, survey_result=survey_result)
        
        text = create_send_info_about_new_survey_result_output(user=user, survey_result=survey_result)
        keyboard = get_keyboard_for_unprocessed_survey_result_actions(link=link)
        
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        send_message = await self.aiogram_wrapper.answer_massage(message=callback.message,
                                                                 text=text,
                                                                 reply_markup=keyboard.as_markup())
        await callback.answer()

    async def _return_to_unprocessed_results(self, callback: CallbackQuery, callback_data: UnprocessedSurveyResultCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.UNPROCESSED_SURVEY_RESULTS)
        await self.manager.launch(name="unprocessed_survey_results",
                                  message=callback.message,
                                  state=state)
        await callback.answer()
