import json
import logging
from typing import TYPE_CHECKING, Callable, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram import F
# from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import AddFilesCallbackFactory
from db.service.abc_services import ABCServices
from db.service.yandex_disk_wrapper import YANDEX_DISK_SESSION
from dtos import SurveyResultComments
from enums import (SURVEY_RESULT_COMMENT_TYPE, RedisTmpFields, ListAddFilesActions)
from keyboards_generators import get_keyboard_for_add_files
from output_generators import create_take_survey_file_count_output, create_add_files_to_survey_result_file_count_output
from resources.messages import (TAKE_SURVEY_SEND_NOT_FILE, ADD_FILES_TO_SURVEY_RESULT, ADD_FILES_FINISH,
                                ADD_FILES_TO_SURVEY_RESULT_DIRECTION_END, ADD_FILED_TO_SURVEY_RESULT_WAIT_END)
from states import States

from .base_command import BaseCommand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .manager import Manager

class AddFilesToSurveyResult(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        self.max_files_count = 20
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_message_handler(self._finish_add_files, States.ADD_FILES_TO_SURVEY_RESULT,
                                                      F.text.lower() == "✅готово")
        self.aiogram_wrapper.register_message_handler(self._process_file, States.ADD_FILES_TO_SURVEY_RESULT)
        self.aiogram_wrapper.register_callback(self._return_to_survey_result_actions, 
                                               AddFilesCallbackFactory.filter(F.action == ListAddFilesActions.RETURN_TO_SURVEY_RESULT_ACTIONS))

    async def execute(self,
                      message: Message,
                      state: FSMContext,
                      command: Optional[CommandObject] = None,
                      survey_result_id: Optional[int] = None,
                      **kwargs):
        # Сохраняем ID результата опроса в состоянии
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.ADD_FILES_TO_SURVEY_RESULT_SURVEY_RESULT_ID.value,
                                                  value=survey_result_id)
        
        # Инициализируем список файлов для накопления
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.ADD_FILES_TO_SURVEY_RESULT_ANSWER.value,
                                                  value={"answer": [],
                                                         "type": SURVEY_RESULT_COMMENT_TYPE.FILES.value})
        
        # Устанавливаем состояние для добавления файлов
        await self.aiogram_wrapper.set_state(state_context=state,
                                             state=States.ADD_FILES_TO_SURVEY_RESULT)
        
        # Отправляем сообщение с инструкциями и клавиатурой
        inline_keyboard, reply_keyboard = get_keyboard_for_add_files()
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=ADD_FILES_TO_SURVEY_RESULT,
                                                                 reply_markup=inline_keyboard.as_markup())
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=ADD_FILES_TO_SURVEY_RESULT_DIRECTION_END,
                                                                 reply_markup=reply_keyboard)

    async def _process_file(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None):
        """Обработка файла"""
        survey_result_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                     field_name=RedisTmpFields.ADD_FILES_TO_SURVEY_RESULT_SURVEY_RESULT_ID.value)
        survey_result = await self.db.survey_result.get_survey_result(id=survey_result_id)
        # Проверяем, что это файл
        if not message.document:
            send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                     text=TAKE_SURVEY_SEND_NOT_FILE)
            return
        
        doc = message.document
        
        # Загружаем файл
        tmp_file_path = await self.aiogram_wrapper.download_file(message=message)
        
        # Создаем путь для файла в хранилище используя существующий метод
        file_s3_path = self.db.files_storage.key_builder.key_survey_file(
            user_id=str(message.chat.id),
            survey_id=str(survey_result.survey_id),
            filename=doc.file_name
        )
        
        # Загружаем файл в хранилище
        await self.db.files_storage.upload_file(object_name=file_s3_path, file_path=tmp_file_path)
        
        # Получаем текущий список файлов
        files_data = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                               field_name=RedisTmpFields.ADD_FILES_TO_SURVEY_RESULT_ANSWER.value)

        # Добавляем новый файл в список
        files_data["answer"].append(file_s3_path)
        
        # Сохраняем обновленный список файлов
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.ADD_FILES_TO_SURVEY_RESULT_ANSWER.value,
                                                  value=files_data)
        
        # Отправляем подтверждение
        text = create_add_files_to_survey_result_file_count_output(len(files_data["answer"]))
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=text)

    async def _finish_add_files(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None):
        """Завершение добавления файлов"""
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=ADD_FILED_TO_SURVEY_RESULT_WAIT_END)

        survey_result_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                     field_name=RedisTmpFields.ADD_FILES_TO_SURVEY_RESULT_SURVEY_RESULT_ID.value)
        survey_result = await self.db.survey_result.get_survey_result(id=survey_result_id)
        # Получаем список файлов
        files_data = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                               field_name=RedisTmpFields.ADD_FILES_TO_SURVEY_RESULT_ANSWER.value)

        # Создаем один объект SurveyResultComments с JSON
        comment = SurveyResultComments(
            survey_result_id=survey_result_id,
            type=SURVEY_RESULT_COMMENT_TYPE.FILES,
            result=json.dumps(files_data, ensure_ascii=False, indent=2)
        )
        
        # Сохраняем в базу данных
        await self.db.survey_result_comments.save_survey_result_comment(survey_result_comment=comment)

        async with YANDEX_DISK_SESSION() as yd:
            await yd.add_files_to_survey_result(services=self.db, survey_result=survey_result, comment=comment)
        
        # Отправляем сообщение о завершении
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=ADD_FILES_FINISH,
                                                                 reply_markup=ReplyKeyboardRemove())
        
        # Возвращаемся к главному меню
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.MAIN_MENU)
        await self.manager.launch(name="main_menu",
                                  message=message,
                                  state=state)

    async def _return_to_survey_result_actions(self, callback, callback_data: AddFilesCallbackFactory, state: FSMContext):
        """Возврат к действиям с результатом опроса"""
        survey_result_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                     field_name=RedisTmpFields.ADD_FILES_TO_SURVEY_RESULT_SURVEY_RESULT_ID.value)
        await self.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                  chat_id=callback.from_user.id)
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.SURVEY_RESULT_ACTIONS)
        message_to_remove_reply_kb = await self.aiogram_wrapper.answer_massage(message=callback.message,
                                                                               text="временное сообщение",
                                                                               reply_markup=ReplyKeyboardRemove())
        await self.manager.aiogram_wrapper.delete_message(message_id=message_to_remove_reply_kb.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="survey_result_actions",
                                  message=callback.message,
                                  state=state,
                                  survey_result_id=survey_result_id)
        await callback.answer()