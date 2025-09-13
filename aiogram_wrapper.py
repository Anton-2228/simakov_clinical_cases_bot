from pathlib import Path
from typing import Optional, Union
import tempfile
import os
import secrets

from aiogram import Bot, Router, Dispatcher
from aiogram.dispatcher.event.handler import CallbackType
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage
from aiogram.types import (InlineKeyboardMarkup, InputMediaAudio,
                           InputMediaDocument, InputMediaPhoto,
                           InputMediaVideo, Message, FSInputFile)

from db.service.abc_services import ABCServices
from states import States


class AiogramWrapper:
    def __init__(self,
                 bot: Bot,
                 db: ABCServices,
                 router: Router,
                 dispatcher: Dispatcher):
        self.bot = bot
        self.db = db
        self.router = router
        self.dispatcher = dispatcher

    async def init_states_data(self, state_context: FSMContext):
        # Тут концептуально должна вызываться инициализация переменных состояния на случай, если где-то
        # они будут нужны в рандомном месте, а явной инициализации нет.
        # По идее надо у каждого класса команды сделать метод для этого и тут вызывать их все, но ща впадлу это делать
        data = await state_context.get_data()

    async def clear_state(self, state_context: FSMContext):
        data = await state_context.get_data()
        await state_context.clear()
        await state_context.set_data(data)

    async def clear_state_and_data(self, state_context: FSMContext):
        await state_context.clear()

    async def set_state(self, state_context: FSMContext, state: States):
        await state_context.set_state(state)

    async def get_state(self, state_context: FSMContext):
        return (await state_context.get_state())

    async def set_state_data(self, state_context: FSMContext, field_name: str, value):
        set_data = {field_name: value}
        await state_context.update_data(**set_data)

    async def get_state_data(self, state_context: FSMContext, field_name: str):
        data = await state_context.get_data()
        assert field_name in data, "Несуществующее поле данных"
        return data[field_name]

    async def delete_message(self, message_id: int, chat_id: int):
        await self.bot.delete_message(chat_id=chat_id, message_id=message_id)

    async def delete_messages(self, message_ids: list[int], chat_id: int):
        for message_id in message_ids:
            await self.bot.delete_message(chat_id=chat_id, message_id=message_id)

    async def answer_massage(self, message: Message, *args, **kwargs) -> SendMessage:
        send_message = await message.answer(*args, **kwargs)
        return send_message

    async def send_message(self,
                          chat_id: int,
                          text: str,
                          reply_markup: Optional[InlineKeyboardMarkup] = None,
                          disable_web_page_preview: Optional[bool] = None) -> tuple[Message, FSMContext]:
        message = await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            disable_web_page_preview=disable_web_page_preview
        )

        state: FSMContext = self.dispatcher.fsm.get_context(
            bot=self.bot,
            chat_id=chat_id,
            user_id=chat_id  # если у тебя личка, то chat_id == user_id
        )

        return message, state

    async def edit_message_reply_markup(self, chat_id: int, message_id: int, reply_markup: Optional[InlineKeyboardMarkup]):
        await self.bot.edit_message_reply_markup(chat_id=chat_id,
                                                 message_id=message_id,
                                                 reply_markup=reply_markup)

    # Пока что хуй забил, гемора много
    async def edit_message(self,
                           message_id: int,
                           chat_id: int,
                           text: str = None,
                           media: Union[
                               InputMediaPhoto,
                               InputMediaVideo,
                               InputMediaAudio,
                               InputMediaDocument
                           ] = None,
                           reply_markup: InlineKeyboardMarkup = None,
                           parse_mode: str = None,
    ):
        if media:
            await self.bot.edit_message_media(
                chat_id=chat_id,
                message_id=message_id,
                media=media,
                reply_markup=reply_markup,
            )
        elif text:
            await self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                parse_mode=parse_mode,
            )
        elif reply_markup:
            await self.bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=reply_markup,
            )
        return

    async def download_file(self, message: Message) -> str:
        """
        Загружает файл из сообщения во временную директорию.
        Возвращает путь к сохраненному файлу с случайным hex-названием.
        """
        if not message.document and not message.photo and not message.video and not message.audio:
            raise ValueError("Сообщение не содержит файл")
        
        # Получаем информацию о файле
        if message.document:
            file_info = message.document
        elif message.photo:
            # Берем фото с максимальным разрешением
            file_info = message.photo[-1]
        elif message.video:
            file_info = message.video
        elif message.audio:
            file_info = message.audio
        else:
            raise ValueError("Неподдерживаемый тип файла")
        
        # Получаем файл от Telegram
        file = await self.bot.get_file(file_info.file_id)
        
        # Создаем временную директорию
        temp_dir = tempfile.mkdtemp()
        
        # Генерируем случайный hex
        random_hex = secrets.token_hex(16)  # 32 символа hex
        
        # Получаем расширение файла из оригинального имени
        original_filename = getattr(file_info, 'file_name', 'file')
        file_extension = os.path.splitext(original_filename)[1] if original_filename else ''
        
        # Формируем путь к файлу
        temp_file_path = os.path.join(temp_dir, f"{random_hex}{file_extension}")
        
        # Скачиваем файл
        await self.bot.download_file(file.file_path, temp_file_path)
        
        return temp_file_path

    async def send_file(self,
                        chat_id: int,
                        file_path: str | Path,
                        caption: Optional[str] = None,
                        reply_markup: Optional[InlineKeyboardMarkup] = None,
                        parse_mode: Optional[str] = None):
        """
        Отправляет файл пользователю. Тип определяется по расширению.
        """
        file_path = str(file_path)
        ext = os.path.splitext(file_path)[1].lower()
        input_file = FSInputFile(file_path)
        return await self.bot.send_document(chat_id,
                                            document=input_file,
                                            caption=caption,
                                            reply_markup=reply_markup,
                                            parse_mode=parse_mode)

    def register_callback(self, callback: CallbackType, *filters: CallbackType):
        self.router.callback_query.register(callback, *filters)

    def register_message_handler(self, handler, *filters, **kwargs):
        self.router.message.register(handler, *filters, **kwargs)
