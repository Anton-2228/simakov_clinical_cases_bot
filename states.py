from aiogram.fsm.state import StatesGroup, State


class States(StatesGroup):
    MAIN_MENU = State()
    REGISTRATION = State()
    EDIT_ADMIN_LIST = State()
    ADD_CLINICAL_CASE = State()
    ADD_USER_TO_ADMIN_LIST = State()
    DELETE_USER_FROM_ADMIN_LIST = State()
    ENTER_NEW_ADMIN = State()
    EDIT_SURVEYS = State()
    ADD_SURVEY = State()
    EDIT_SURVEY = State()
