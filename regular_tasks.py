from aiogram_wrapper import AiogramWrapper
from commands import Manager
from db.postgres_models import MessageType, MessageStatus
from db.service.abc_services import ABCServices
from enums import USER_TYPE
from keyboards_generators import get_keyboard_for_reply_message_to_client



class RegularTasks:
    def __init__(self, db: ABCServices, aiogram_wrapper: AiogramWrapper, manager: Manager):
        self.db = db
        self.aiogram_wrapper = aiogram_wrapper
        self.manager = manager
