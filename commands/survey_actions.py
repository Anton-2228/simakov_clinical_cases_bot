import logging
from typing import TYPE_CHECKING, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import SurveyActionsCallbackFactory
from db.service.abc_services import ABCServices
from enums import ListSurveyActionsActions, RedisTmpFields
from keyboards_generators import get_keyboard_for_survey_actions
from resources.messages import SURVEY_ACTIONS
from states import States

from .base_command import BaseCommand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .manager import Manager

class SurveyActions(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_callback(self._take_survey, SurveyActionsCallbackFactory.filter(F.action == ListSurveyActionsActions.TAKE_SURVEY))
        self.aiogram_wrapper.register_callback(self._view_completed_surveys, SurveyActionsCallbackFactory.filter(F.action == ListSurveyActionsActions.VIEW_COMPLETED_SURVEYS))
        self.aiogram_wrapper.register_callback(self._return_to_main_menu, SurveyActionsCallbackFactory.filter(F.action == ListSurveyActionsActions.RETURN_TO_MAIN_MENU))

    async def execute(self,
                      message: Message,
                      state: FSMContext,
                      command: Optional[CommandObject] = None,
                      survey_id: Optional[int] = None,
                      **kwargs):
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.SURVEY_ACTIONS_SURVEY_ID.value,
                                                  value=survey_id)
        keyboard = get_keyboard_for_survey_actions()
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=SURVEY_ACTIONS,
                                                                 reply_markup=keyboard.as_markup())

    async def _take_survey(self, callback: CallbackQuery, callback_data: SurveyActionsCallbackFactory, state: FSMContext):
        survey_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                              field_name=RedisTmpFields.SURVEY_ACTIONS_SURVEY_ID.value)
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.SELECT_TAKE_SURVEY)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="take_survey",
                                  message=callback.message,
                                  state=state,
                                  survey_id=survey_id)
        await callback.answer()

    async def _view_completed_surveys(self, callback: CallbackQuery, callback_data: SurveyActionsCallbackFactory, state: FSMContext):
        survey_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                              field_name=RedisTmpFields.SURVEY_ACTIONS_SURVEY_ID.value)
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.SELECT_SURVEY_RESULT)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="select_survey_result",
                                  message=callback.message,
                                  state=state,
                                  survey_id=survey_id)
        await callback.answer()

    async def _return_to_main_menu(self, callback: CallbackQuery, callback_data: SurveyActionsCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.SELECT_TAKE_SURVEY)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="select_take_survey",
                                  message=callback.message,
                                  state=state)
        await callback.answer()