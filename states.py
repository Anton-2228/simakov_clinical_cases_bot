from aiogram.fsm.state import StatesGroup, State


class States(StatesGroup):
    MAIN_MENU = State()
    REGISTRATION = State()
    EDIT_ADMIN_LIST = State()
    ADD_CLINICAL_CASE = State()
    ENTER_NEW_ADMIN = State()
