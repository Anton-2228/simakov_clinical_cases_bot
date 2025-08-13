from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks_factories import UserMainMenuCallbackFactory, AdminMainMenuCallbackFactory, EditAdminListCallbackFactory, \
    AddUserToAdminListCallbackFactory
from enums import ListUserMainMenuActions, ListAdminMainMenuActions, ListEditAdminListActions, \
    ListAddUserToAdminListActions


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

def get_keyboard_for_edit_admin_list() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="Add User", callback_data=EditAdminListCallbackFactory(action=ListEditAdminListActions.ADD_ADMIN))
    builder.button(text="Remove User", callback_data=EditAdminListCallbackFactory(action=ListEditAdminListActions.REMOVE_ADMIN))
    builder.button(text="Return to the main menu", callback_data=EditAdminListCallbackFactory(action=ListEditAdminListActions.RETURN_TO_MAIN_MENU))
    builder.adjust(2, 1)
    return builder

def get_keyboard_for_add_user_to_admin_list() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Return", callback_data=AddUserToAdminListCallbackFactory(action=ListAddUserToAdminListActions.RETURN_TO_EDIT_ADMIN_LIST).pack()))
    builder.adjust(1)
    return builder
