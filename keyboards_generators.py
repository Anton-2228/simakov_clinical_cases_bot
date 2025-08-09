from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks_factories import UserMainMenuCallbackFactory, AdminMainMenuCallbackFactory
from enums import ListUserMainMenuActions, ListAdminMainMenuActions


def get_keyboard_for_user_main_menu() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="Добавить клинический случай", callback_data=UserMainMenuCallbackFactory(action=ListUserMainMenuActions.ADD_CLINICAL_CASE))
    builder.adjust(1)
    return builder

def get_keyboard_for_admin_main_menu() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="Добавить клинический случай", callback_data=AdminMainMenuCallbackFactory(action=ListAdminMainMenuActions.ADD_CLINICAL_CASE))
    builder.button(text="Обновить список админов", callback_data=AdminMainMenuCallbackFactory(action=ListAdminMainMenuActions.EDIT_ADMIN_LIST))
    builder.adjust(1)
    return builder
