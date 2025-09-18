from abc import ABC, abstractmethod
from typing import Optional, List
from users.domain.entities.user_entity import UserEntity
class IUserRepository(ABC):

    @abstractmethod
    def create(self, user: UserEntity) -> UserEntity:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> UserEntity | None:
        pass
    
    @abstractmethod
    def get_by_id(self, id:str) -> UserEntity | None:
        pass

    @abstractmethod
    def get_all_users(self) -> Optional[List[UserEntity]]:
        pass

    @abstractmethod
    def update_user(self, user:UserEntity) -> Optional[UserEntity]:
        pass

    @abstractmethod
    def delete_user(self, id:str) -> None:
        pass

    @abstractmethod
    def recover_password(self, email: str, password: str) -> UserEntity:
        pass

    @abstractmethod
    def update_password(self, id:str, password: str) -> UserEntity:
        pass
