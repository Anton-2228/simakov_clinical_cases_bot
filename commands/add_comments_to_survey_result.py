import json
import logging
from typing import TYPE_CHECKING, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import AddCommentsCallbackFactory
from db.service.abc_services import ABCServices
from db.service.yandex_disk_wrapper import YANDEX_DISK_SESSION
from dtos import SurveyResultComments
from enums import (SURVEY_RESULT_COMMENT_TYPE, RedisTmpFields, ListAddCommentsActions)
from keyboards_generators import get_keyboard_for_add_comments
from resources.messages import (TAKE_SURVEY_SEND_NOT_TEXT, ADD_COMMENTS_TO_SURVEY_RESULT, ADD_COMMENTS_FINISH,
                                ADD_COMMENTS_TO_SURVEY_RESULT_WAIT_END)
from states import States

from .base_command import BaseCommand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .manager import Manager

class AddCommentsToSurveyResult(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        self.max_files_count = 20
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_message_handler(self._process_comment, States.ADD_COMMENTS_TO_SURVEY_RESULT)
        self.aiogram_wrapper.register_callback(self._return_to_survey_result_actions, 
                                               AddCommentsCallbackFactory.filter(F.action == ListAddCommentsActions.RETURN_TO_SURVEY_RESULT_ACTIONS))

    async def execute(self,
                      message: Message,
                      state: FSMContext,
                      command: Optional[CommandObject] = None,
                      survey_result_id: Optional[int] = None,
                      **kwargs):
        # Сохраняем ID результата опроса в состоянии
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.ADD_COMMENTS_TO_SURVEY_RESULT_SURVEY_RESULT_ID.value,
                                                  value=survey_result_id)
        
        # Устанавливаем состояние для добавления комментариев
        await self.aiogram_wrapper.set_state(state_context=state,
                                             state=States.ADD_COMMENTS_TO_SURVEY_RESULT)
        
        # Отправляем сообщение с инструкциями и клавиатурой
        keyboard = get_keyboard_for_add_comments()
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=ADD_COMMENTS_TO_SURVEY_RESULT,
                                                                 reply_markup=keyboard.as_markup())

    async def _process_comment(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None):
        """Обработка текстового комментария"""
        survey_result_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                     field_name=RedisTmpFields.ADD_COMMENTS_TO_SURVEY_RESULT_SURVEY_RESULT_ID.value)
        
        # Проверяем, что это текст
        if message.text and message.text.strip():
            await self._process_text_comment(message=message, state_context=state, survey_result_id=survey_result_id)
        else:
            # Если не текст, отправляем ошибку
            send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                     text=TAKE_SURVEY_SEND_NOT_TEXT)

    async def _process_text_comment(self, message: Message, state_context: FSMContext, survey_result_id: int):
        """Обработка текстового комментария"""
        comment_text = message.text.strip()

        survey_result = await self.db.survey_result.get_survey_result(id=survey_result_id)

        # Создаем комментарий (текстовые комментарии не сохраняются в minio)
        result_data = json.dumps({"type": SURVEY_RESULT_COMMENT_TYPE.STRING.value,
                                  "answer": comment_text})
        comment = SurveyResultComments(
            survey_result_id=survey_result_id,
            type=SURVEY_RESULT_COMMENT_TYPE.STRING,
            result=result_data
        )

        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=ADD_COMMENTS_TO_SURVEY_RESULT_WAIT_END)

        # Сохраняем в базу данных
        comment = await self.db.survey_result_comments.save_survey_result_comment(survey_result_comment=comment)

        async with YANDEX_DISK_SESSION() as yd:
            await yd.add_comment_to_survey_result(services=self.db, survey_result=survey_result, comment=comment)

        # Отправляем сообщение о завершении
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=ADD_COMMENTS_FINISH)

        # Возвращаемся к главному меню
        await self.manager.aiogram_wrapper.set_state(state_context=state_context,
                                                     state=States.MAIN_MENU)
        await self.manager.launch(name="main_menu",
                                  message=message,
                                  state=state_context)

    async def _return_to_survey_result_actions(self, callback, callback_data: AddCommentsCallbackFactory, state: FSMContext):
        """Возврат к действиям с результатом опроса"""
        survey_result_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                     field_name=RedisTmpFields.ADD_COMMENTS_TO_SURVEY_RESULT_SURVEY_RESULT_ID.value)
        
        # Удаляем сообщение с клавиатурой
        await self.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                  chat_id=callback.from_user.id)
        
        # Возвращаемся к действиям с результатом опроса
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.SURVEY_RESULT_ACTIONS)
        await self.manager.launch(name="survey_result_actions",
                                  message=callback.message,
                                  state=state,
                                  survey_result_id=survey_result_id)
        await callback.answer()