import asyncio
import logging
from collections import defaultdict
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
from keyboards_generators import get_keyboard_for_reply_message_to_client
from models import User
from output_generators import create_message_to_admins_output
from resources.messages import MESSAGE_TO_USER, BROKEN_MARKDOWN
from states import States


logger = logging.getLogger(__name__)


class AiogramWrapper:
    _album_cache: dict[tuple[int, str], list[Message]] = defaultdict(list)
    _ALBUM_WAIT_MS = 400  # задержка, чтобы собрать все части альбома
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
        if field_name not in data:
            logger.info(f"get_state_data Несуществующее поле данных {field_name}")
            return
        # assert field_name in data, "Несуществующее поле данных"
        return data[field_name]

    async def delete_message(self, message_id: int, chat_id: int):
        await self.bot.delete_message(chat_id=chat_id, message_id=message_id)

    async def delete_messages(self, message_ids: list[int], chat_id: int):
        for message_id in message_ids:
            await self.bot.delete_message(chat_id=chat_id, message_id=message_id)

    async def answer_massage(self, message: Message, *args, **kwargs) -> SendMessage:
        send_message = await message.answer(*args, **kwargs)
        return send_message

    async def answer_photo_massage(self, message: Message, *args, **kwargs) -> SendMessage:
        send_message = await message.answer_photo(*args, **kwargs)
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

    @staticmethod
    def _to_input_media(m: Message):
        """
        Преобразует Message в соответствующий InputMedia*
        Поддержаны: фото, видео, документ, аудио с сохранением caption/caption_entities
        """
        caption = m.caption or None
        entities = m.caption_entities or None

        if m.photo:
            file_id = m.photo[-1].file_id
            return InputMediaPhoto(media=file_id, caption=caption, caption_entities=entities)
        if m.video:
            return InputMediaVideo(media=m.video.file_id, caption=caption, caption_entities=entities)
        if m.document:
            return InputMediaDocument(media=m.document.file_id, caption=caption, caption_entities=entities)
        if m.audio:
            return InputMediaAudio(media=m.audio.file_id, caption=caption, caption_entities=entities)
        return None

    async def _flush_album(self, key: tuple[int, str], to_user_id: int) -> list[Message]:
        messages = self._album_cache.pop(key, [])
        if not messages:
            return []

        media = []
        singles_fallback = []
        for m in messages:
            im = self._to_input_media(m)
            if im:
                media.append(im)
            else:
                singles_fallback.append(m)

        delivered: list[Message] = []
        if media:
            sent = await self.bot.send_media_group(chat_id=to_user_id, media=media)
            delivered.extend(sent)

        for m in singles_fallback if media else messages:
            delivered.append(await m.copy_to(chat_id=to_user_id))
        return delivered

    async def _send_preserving_entities(  # NEW
            self,
            message: Message,
            to_user_id: int,
            reply_to_message_id: Optional[int] = None,
            attach_markup: bool = False,
    ) -> Optional[Message]:
        """
        Явно переотправляет контент, сохраняя entities/caption_entities.
        Возвращает Message или None, если тип не поддержан здесь.
        """
        markup = message.reply_markup if attach_markup else None

        if message.text:
            # Сохраняем все entities
            return await self.bot.send_message(
                chat_id=to_user_id,
                text=message.text,
                entities=message.entities,
                reply_to_message_id=reply_to_message_id,
                reply_markup=markup,
            )

        if message.photo:
            return await self.bot.send_photo(
                chat_id=to_user_id,
                photo=message.photo[-1].file_id,
                caption=message.caption,
                caption_entities=message.caption_entities,
                reply_to_message_id=reply_to_message_id,
                reply_markup=markup,
            )
        if message.video:
            return await self.bot.send_video(
                chat_id=to_user_id,
                video=message.video.file_id,
                caption=message.caption,
                caption_entities=message.caption_entities,
                reply_to_message_id=reply_to_message_id,
                reply_markup=markup,
            )
        if message.document:
            return await self.bot.send_document(
                chat_id=to_user_id,
                document=message.document.file_id,
                caption=message.caption,
                caption_entities=message.caption_entities,
                reply_to_message_id=reply_to_message_id,
                reply_markup=markup,
            )
        if message.audio:
            return await self.bot.send_audio(
                chat_id=to_user_id,
                audio=message.audio.file_id,
                caption=message.caption,
                caption_entities=message.caption_entities,
                reply_to_message_id=reply_to_message_id,
                reply_markup=markup,
            )
        # Голосовые/видео-заметки/стикеры/локации оставим copy_to
        return None

    async def relay_to_user(
            self,
            message: Message,
            to_user_id: int,
            *,
            reply_to_message_id: Optional[int] = None,
            preserve_forward_header: bool = False,
            attach_markup: bool = False,  # NEW: если хочешь тащить исходную клавиатуру
    ) -> list[Message]:
        """
        Универсальная пересылка входящего message другому пользователю.
        - Альбомы: собирает по media_group_id и отправляет send_media_group.
        - Текст/медиа с разметкой: отправляет вручную с entities для гарантии.
        - Остальное: copy_to/forward.
        """
        # Альбом
        if message.media_group_id:
            key = (message.chat.id, message.media_group_id)
            self._album_cache[key].append(message)
            if len(self._album_cache[key]) == 1:
                await asyncio.sleep(self._ALBUM_WAIT_MS / 1000)
                return await self._flush_album(key, to_user_id)
            return []

        # Попытка гарантированного сохранения разметки
        # Если есть entities/caption_entities — шлём вручную
        if (message.text and message.entities) or (message.caption and message.caption_entities):
            sent = await self._send_preserving_entities(
                message=message,
                to_user_id=to_user_id,
                reply_to_message_id=reply_to_message_id,
                attach_markup=attach_markup,
            )
            if sent:
                return [sent]

        # Иначе обычное копирование/пересылка
        if preserve_forward_header:
            return [await message.forward(chat_id=to_user_id)]

        return [await message.copy_to(
            chat_id=to_user_id,
            reply_to_message_id=reply_to_message_id
        )]

    async def send_message_to_admins(
            self,
            message: Message,
            admin_telegram_id: int,
            from_user: User,
            *,
            reply_to_message_id: Optional[int] = None,
            preserve_forward_header: bool = False,
            attach_markup: bool = False,  # NEW: если хочешь тащить исходную клавиатуру
    ):
        delivered = await self.relay_to_user(
            message=message,
            to_user_id=admin_telegram_id,
            reply_to_message_id=reply_to_message_id,
            preserve_forward_header=preserve_forward_header,
            attach_markup=attach_markup,  # если хочешь повторить inline-кнопки
        )
        keyboard = get_keyboard_for_reply_message_to_client(from_user_id=message.chat.id)
        text = create_message_to_admins_output(user=from_user)
        await self.send_message(chat_id=admin_telegram_id,
                                text=text,
                                reply_markup=keyboard.as_markup())
        return delivered

    async def send_message_to_user(
            self,
            message: Message,
            user_telegram_id: int,
            *,
            reply_to_message_id: Optional[int] = None,
            preserve_forward_header: bool = False,
            attach_markup: bool = False,  # NEW: если хочешь тащить исходную клавиатуру
    ):
        await self.send_message(chat_id=user_telegram_id,
                                text=MESSAGE_TO_USER)
        delivered = await self.relay_to_user(
            message=message,
            to_user_id=user_telegram_id,
            reply_to_message_id=reply_to_message_id,
            preserve_forward_header=preserve_forward_header,
            attach_markup=attach_markup,  # если хочешь повторить inline-кнопки
        )
        return delivered

    def register_callback(self, callback: CallbackType, *filters: CallbackType):
        self.router.callback_query.register(callback, *filters)

    def register_message_handler(self, handler, *filters, **kwargs):
        self.router.message.register(handler, *filters, **kwargs)

    async def _check_validity_of_message(self, message: Message, text: str) -> Optional[Message]:
        try:
            m = await message.answer(text=text)
            await self.delete_message(message_id=m.message_id, chat_id=m.chat.id)
        except Exception as e:
            error_message = await message.answer(text=BROKEN_MARKDOWN)
            return error_message
