from typing import Optional

from aiogram.filters.callback_data import CallbackData

from enums import ListUserMainMenuActions, ListAdminMainMenuActions


class UserMainMenuCallbackFactory(CallbackData, prefix="user_main_menu"):
    action: ListUserMainMenuActions

class AdminMainMenuCallbackFactory(CallbackData, prefix="admin_main_menu"):
    action: ListAdminMainMenuActions