from typing import Optional, Union

from aiogram import Bot, Router
from aiogram.dispatcher.event.handler import CallbackType
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage
from aiogram.types import (InlineKeyboardMarkup, InputMediaAudio,
                           InputMediaDocument, InputMediaPhoto,
                           InputMediaVideo, Message)

from db.service.abc_services import ABCServices
from states import States


class AiogramWrapper:
    def __init__(self,
                 bot: Bot,
                 db: ABCServices,
                 router: Router):
        self.bot = bot
        self.db = db
        self.router = router

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

    def register_callback(self, callback: CallbackType, *filters: CallbackType):
        self.router.callback_query.register(callback, *filters)

    def register_message_handler(self, handler, *filters, **kwargs):
        self.router.message.register(handler, *filters, **kwargs)
