from aiogram_wrapper import AiogramWrapper
from commands import Manager
from db.postgres_models import MessageType, MessageStatus
from db.service.abc_services import ABCServices
from enums import USER_TYPE
from keyboards_generators import get_keyboard_for_reply_message_to_client

from output_generators import create_message_to_admins_output, create_message_to_user_output


class RegularTasks:
    def __init__(self, db: ABCServices, aiogram_wrapper: AiogramWrapper, manager: Manager):
        self.db = db
        self.aiogram_wrapper = aiogram_wrapper
        self.manager = manager

    async def send_messages_to_admins(self):
        new_messages = await self.db.message.get_messages_by_type_and_status(message_type=MessageType.TO_ADMINS,
                                                                             status=MessageStatus.NEW)
        if len(new_messages) == 0:
            return

        admins = await self.db.user.get_users_by_type(user_type=USER_TYPE.ADMIN)
        for new_message in new_messages:
            user = await self.db.user.get_user(telegram_id=new_message.from_user_id)
            keyboard = get_keyboard_for_reply_message_to_client(from_user_id=new_message.from_user_id)
            text = create_message_to_admins_output(user=user,
                                                   text=new_message.text)
            for admin in admins:
                await self.aiogram_wrapper.send_message(chat_id=admin.telegram_id,
                                                        text=text,
                                                        reply_markup=keyboard.as_markup())
            new_message.status = MessageStatus.SENT
            await self.db.message.update_message(message=new_message)

    async def send_messages_to_users(self):
        new_messages = await self.db.message.get_messages_by_type_and_status(message_type=MessageType.TO_USER,
                                                                             status=MessageStatus.NEW)
        if len(new_messages) == 0:
            return

        users = await self.db.user.get_users()
        for new_message in new_messages:
            for user in users:
                if new_message.to_user_id == user.telegram_id:
                    text = create_message_to_user_output(text=new_message.text)
                    await self.aiogram_wrapper.send_message(chat_id=user.telegram_id,
                                                            text=text)
                    break
            new_message.status = MessageStatus.SENT
            await self.db.message.update_message(message=new_message)
