import logging
from typing import TYPE_CHECKING, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage
from aiogram.types import CallbackQuery, Message
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import AddUserToAdminListCallbackFactory, ProcessingSurveyResultCallbackFactory
from db.postgres_models import SurveyResultStatus
from db.service.abc_services import ABCServices
from enums import (USER_TYPE, ListAddUserToAdminListActions,
                   RedisTmpFields, ListProcessingSurveyResultsActions)
from keyboards_generators import get_keyboard_for_add_user_to_admin_list
from output_generators import create_processed_survey_results_output
from resources.messages import (ENTER_NEW_ADMIN_NOT_REGISTERED_USER_MESSAGE,
                                ENTER_NEW_ADMIN_NOT_VALID_TG_ID_MESSAGE,
                                REQUEST_ENTER_NEW_ADMIN_MESSAGE, SET_RESULT_SURVEY_STATUS_STATUS_ALREADY_EXIST)
from states import States

from .base_command import BaseCommand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .manager import Manager

class ProcessingSurveyResults(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_callback(self._accept_publication, ProcessingSurveyResultCallbackFactory.filter(F.action == ListProcessingSurveyResultsActions.ACCEPTED_PUBLICATION))
        self.aiogram_wrapper.register_callback(self._accept_archive, ProcessingSurveyResultCallbackFactory.filter(F.action == ListProcessingSurveyResultsActions.ACCEPTED_ARCHIVE))
        self.aiogram_wrapper.register_callback(self._no_accept, ProcessingSurveyResultCallbackFactory.filter(F.action == ListProcessingSurveyResultsActions.NOT_ACCEPTED))

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None, **kwargs):
        pass

    async def _accept_publication(self, callback: CallbackQuery, callback_data: ProcessingSurveyResultCallbackFactory, state: FSMContext):
        survey_result = await self.db.survey_result.get_survey_result(id=callback_data.survey_result_id)
        if len(survey_result.statuses) != 0:
            message_to_remove_reply_kb = await self.aiogram_wrapper.answer_massage(message=callback.message,
                                                                                   text=SET_RESULT_SURVEY_STATUS_STATUS_ALREADY_EXIST)
            await callback.answer()
            return
        survey_result.statuses = [SurveyResultStatus.ACCEPTED_PUBLICATION]
        await self.db.survey_result.update_survey_result(survey_result=survey_result)
        text = create_processed_survey_results_output(survey_result.statuses)
        await self.aiogram_wrapper.answer_massage(message=callback.message,
                                                  text=text)
        await callback.answer()

    async def _accept_archive(self, callback: CallbackQuery, callback_data: ProcessingSurveyResultCallbackFactory, state: FSMContext):
        survey_result = await self.db.survey_result.get_survey_result(id=callback_data.survey_result_id)
        if len(survey_result.statuses) != 0:
            message_to_remove_reply_kb = await self.aiogram_wrapper.answer_massage(message=callback.message,
                                                                                   text=SET_RESULT_SURVEY_STATUS_STATUS_ALREADY_EXIST)
            await callback.answer()
            return
        survey_result.statuses = [SurveyResultStatus.ACCEPTED_PUBLICATION, SurveyResultStatus.ACCEPTED_ARCHIVE]
        await self.db.survey_result.update_survey_result(survey_result=survey_result)
        text = create_processed_survey_results_output(survey_result.statuses)
        await self.aiogram_wrapper.answer_massage(message=callback.message,
                                                  text=text)
        await callback.answer()

    async def _no_accept(self, callback: CallbackQuery, callback_data: ProcessingSurveyResultCallbackFactory, state: FSMContext):
        survey_result = await self.db.survey_result.get_survey_result(id=callback_data.survey_result_id)
        if len(survey_result.statuses) != 0:
            message_to_remove_reply_kb = await self.aiogram_wrapper.answer_massage(message=callback.message,
                                                                                   text=SET_RESULT_SURVEY_STATUS_STATUS_ALREADY_EXIST)
            await callback.answer()
            return
        survey_result.statuses = [SurveyResultStatus.NOT_ACCEPTED]
        await self.db.survey_result.update_survey_result(survey_result=survey_result)
        text = create_processed_survey_results_output(survey_result.statuses)
        await self.aiogram_wrapper.answer_massage(message=callback.message,
                                                  text=text)
        await callback.answer()
