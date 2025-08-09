from abc import abstractmethod, ABC

from db.service.user.async_user_service import AsyncUserService
from db.service.user.user_service import UserService


class Services(ABC):
    @property
    @abstractmethod
    def user(self) -> UserService | AsyncUserService:
        pass
