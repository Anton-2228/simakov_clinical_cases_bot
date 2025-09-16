import json
import logging
from typing import TYPE_CHECKING, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import SurveyResultActionsCallbackFactory
from db.service.abc_services import ABCServices
from db.service.yandex_disk_wrapper import YANDEX_DISK_SESSION
from enums import ListSurveyResultActionsActions, RedisTmpFields, SURVEY_STEP_TYPE
from keyboards_generators import (get_keyboard_for_survey_result_actions,
                                  get_keyboard_for_confirm_delete_survey_result)
from output_generators import create_survey_result_see_answers_output
from resources.messages import SURVEY_RESULT_ACTIONS, CONFIRM_DELETE_SURVEY_RESULT
from states import States
from utils import get_tmp_path

from .base_command import BaseCommand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .manager import Manager

class SurveyResultActions(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_callback(self._delete_result, SurveyResultActionsCallbackFactory.filter(F.action == ListSurveyResultActionsActions.DELETE_RESULT))
        self.aiogram_wrapper.register_callback(self._confirm_delete_result, SurveyResultActionsCallbackFactory.filter(F.action == ListSurveyResultActionsActions.CONFIRM_DELETE_RESULT))
        self.aiogram_wrapper.register_callback(self._reject_delete_result, SurveyResultActionsCallbackFactory.filter(F.action == ListSurveyResultActionsActions.REJECT_DELETE_RESULT))
        self.aiogram_wrapper.register_callback(self._see_answers, SurveyResultActionsCallbackFactory.filter(F.action == ListSurveyResultActionsActions.SEE_ANSWERS))
        self.aiogram_wrapper.register_callback(self._add_comments, SurveyResultActionsCallbackFactory.filter(F.action == ListSurveyResultActionsActions.ADD_COMMENTS))
        self.aiogram_wrapper.register_callback(self._add_files, SurveyResultActionsCallbackFactory.filter(F.action == ListSurveyResultActionsActions.ADD_FILES))
        self.aiogram_wrapper.register_callback(self._return_to_select_survey_result, SurveyResultActionsCallbackFactory.filter(F.action == ListSurveyResultActionsActions.RETURN_TO_SELECT_SURVEY_RESULT))

    async def execute(self,
                      message: Message,
                      state: FSMContext,
                      command: Optional[CommandObject] = None,
                      survey_result_id: Optional[int] = None,
                      **kwargs):
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.SURVEY_RESULT_ACTIONS_SURVEY_RESULT_ID.value,
                                                  value=survey_result_id)
        keyboard = get_keyboard_for_survey_result_actions()
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=SURVEY_RESULT_ACTIONS,
                                                                 reply_markup=keyboard.as_markup())

    async def _delete_result(self, callback: CallbackQuery, callback_data: SurveyResultActionsCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        keyboard = get_keyboard_for_confirm_delete_survey_result()
        send_message = await self.aiogram_wrapper.answer_massage(message=callback.message,
                                                                 text=CONFIRM_DELETE_SURVEY_RESULT,
                                                                 reply_markup=keyboard.as_markup())
        await callback.answer()

    async def _confirm_delete_result(self, callback: CallbackQuery, callback_data: SurveyResultActionsCallbackFactory, state: FSMContext):
        survey_result_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                     field_name=RedisTmpFields.SURVEY_RESULT_ACTIONS_SURVEY_RESULT_ID.value)
        survey_result = await self.db.survey_result.get_survey_result(id=survey_result_id)
        await self.db.survey_result.delete_survey_result(id=survey_result_id)
        async with YANDEX_DISK_SESSION() as yd:
            await yd.delete_survey_result(services=self.db, survey_result=survey_result)
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.SELECT_SURVEY_RESULT)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="select_survey_result",
                                  message=callback.message,
                                  state=state,
                                  survey_id=survey_result.survey_id)
        await callback.answer()

    async def _reject_delete_result(self, callback: CallbackQuery, callback_data: SurveyResultActionsCallbackFactory, state: FSMContext):
        survey_result_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                     field_name=RedisTmpFields.SURVEY_RESULT_ACTIONS_SURVEY_RESULT_ID.value)
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.SURVEY_RESULT_ACTIONS)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="survey_result_actions",
                                  message=callback.message,
                                  state=state,
                                  survey_result_id=survey_result_id)
        await callback.answer()

    async def _see_answers(self, callback: CallbackQuery, callback_data: SurveyResultActionsCallbackFactory, state: FSMContext):
        survey_result_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                     field_name=RedisTmpFields.SURVEY_RESULT_ACTIONS_SURVEY_RESULT_ID.value)
        survey_result = await self.db.survey_result.get_survey_result(id=survey_result_id)
        for survey_step_result in survey_result.survey_step_results:
            survey_step = await self.db.survey_step.get_survey_step(id=survey_step_result.survey_step_id)
            text_output = create_survey_result_see_answers_output(step=survey_step,
                                                                  step_result=survey_step_result)
            if survey_step.type == SURVEY_STEP_TYPE.STRING:
                await self.aiogram_wrapper.answer_massage(message=callback.message,
                                                          text=text_output)
            elif survey_step.type == SURVEY_STEP_TYPE.FILES:
                await self.aiogram_wrapper.answer_massage(message=callback.message,
                                                          text=text_output)
                answer = json.loads(survey_step_result.result)
                for minio_key in answer["answer"]:
                    tmp_path = get_tmp_path(filename=minio_key.split("/")[-1])
                    await self.db.files_storage.download_file(object_name=minio_key,
                                                              file_path=tmp_path)
                    await self.aiogram_wrapper.send_file(chat_id=callback.message.chat.id,
                                                         file_path=tmp_path)
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.SURVEY_RESULT_ACTIONS)
        # await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
        #                                                   chat_id=callback.from_user.id)
        await self.manager.launch(name="survey_result_actions",
                                  message=callback.message,
                                  state=state,
                                  survey_result_id=survey_result_id)
        await callback.answer()

    async def _add_comments(self, callback: CallbackQuery, callback_data: SurveyResultActionsCallbackFactory, state: FSMContext):
        survey_result_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                    field_name=RedisTmpFields.SURVEY_RESULT_ACTIONS_SURVEY_RESULT_ID.value)
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.ADD_COMMENTS_TO_SURVEY_RESULT)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="add_comments_to_survey_result",
                                  message=callback.message,
                                  state=state,
                                  survey_result_id=survey_result_id)
        await callback.answer()

    async def _add_files(self, callback: CallbackQuery, callback_data: SurveyResultActionsCallbackFactory, state: FSMContext):
        survey_result_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                    field_name=RedisTmpFields.SURVEY_RESULT_ACTIONS_SURVEY_RESULT_ID.value)
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.ADD_FILES_TO_SURVEY_RESULT)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="add_files_to_survey_result",
                                  message=callback.message,
                                  state=state,
                                  survey_result_id=survey_result_id)
        await callback.answer()

    async def _return_to_select_survey_result(self, callback: CallbackQuery, callback_data: SurveyResultActionsCallbackFactory, state: FSMContext):
        survey_result_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                     field_name=RedisTmpFields.SURVEY_RESULT_ACTIONS_SURVEY_RESULT_ID.value)
        survey_result = await self.db.survey_result.get_survey_result(id=survey_result_id)
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.SELECT_SURVEY_RESULT)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="select_survey_result",
                                  message=callback.message,
                                  state=state,
                                  survey_id=survey_result.survey_id)
        await callback.answer()
