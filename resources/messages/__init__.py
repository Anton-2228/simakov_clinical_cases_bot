from pathlib import Path

from utils import load_txt

HELLO_MESSAGE = load_txt(Path(__file__).parent / "HELLO.txt")
USER_MAIN_MENU_MESSAGE = load_txt(Path(__file__).parent / "USER_MAIN_MENU.txt")
ADMIN_MAIN_MENU_MESSAGE = load_txt(Path(__file__).parent / "ADMIN_MAIN_MENU.txt")
REGISTRATION_MESSAGE = load_txt(Path(__file__).parent / "REGISTRATION.txt")
REGISTRATION_NOT_VALID_FULL_NAME_MESSAGE = load_txt(Path(__file__).parent / "errors/REGISTRATION_NOT_VALID_FULL_NAME.txt")
EDIT_ADMIN_LIST_MESSAGE = load_txt(Path(__file__).parent / "EDIT_ADMIN_LIST_MESSAGE.txt")
REQUEST_ENTER_NEW_ADMIN_MESSAGE = load_txt(Path(__file__).parent / "REQUEST_ENTER_NEW_ADMIN.txt")
ENTER_NEW_ADMIN_NOT_VALID_TG_ID_MESSAGE = load_txt(Path(__file__).parent / "errors/ENTER_NEW_ADMIN_NOT_VALID_TG_ID.txt")
ENTER_NEW_ADMIN_NOT_REGISTERED_USER_MESSAGE = load_txt(Path(__file__).parent / "errors/ENTER_NEW_ADMIN_NOT_REGISTERED_USER.txt")
REMOVE_ADMIN_MESSAGE = load_txt(Path(__file__).parent / "REMOVE_ADMIN.txt")
EDIT_CLINICAL_CASES_SURVEY_MESSAGE = load_txt(Path(__file__).parent / "EDIT_CLINICAL_CASES_SURVEY.txt")
