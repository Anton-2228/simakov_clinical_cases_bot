from enum import Enum


class USER_TYPE(Enum):
    ADMIN = "admin"
    CLIENT = "client"

class ListUserMainMenuActions(Enum):
    ADD_CLINICAL_CASE = "add_clinical_case"

class ListAdminMainMenuActions(Enum):
    ADD_CLINICAL_CASE = "add_clinical_case"
    EDIT_ADMIN_LIST = "edit_admin_list"
