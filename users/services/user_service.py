from typing import List, Optional
from uuid import UUID
from datetime import datetime
from django.contrib.auth.hashers import make_password, check_password
from users.domain.contracts.iuser_repository import IUserRepository
from users.domain.entities.user_entity import UserEntity

class UserService:
    def __init__(self, user_repository:IUserRepository):
        self.user_repository =user_repository
    
    def create_user(self, name: str, last_name: str, email: str, password: str):
        
        now = datetime.now()

        user_entity = UserEntity(
            id="",
            name=name,
            last_name=last_name,
            email=email,
            password=make_password(password),
            created_at=now,
            updated_at=now
        )
        
        get_user_by_email = self.user_repository.get_by_email(email=email)

        if get_user_by_email:
            raise ValueError("Já existe um usuário com esse email🚫")
        
        #Depois deve ser feito o envio de email para confirmar ao usuário o seu cadastro
        
        user = self.user_repository.create(user_entity)

        return user
    
    def get_user_by_id(self, id: UUID)-> Optional[UserEntity]:
        user = self.user_repository.get_by_id(id=id)

        if not user:
            raise ValueError("Usuário não encontrado🛑")
        
        return user
    
    def get_all_users(self) -> Optional[List[UserEntity]]:
        users = self.user_repository.get_all_users()

        if not users:
            return []

        return users
    
    def update_user_data(
            self,
            id: UUID, 
            name:Optional[str] = None, 
            last_name: Optional[str] = None, 
            email: Optional[str] = None, 
        ) -> Optional[UserEntity]:

            existing_user = self.user_repository.get_by_id(id)

            if not existing_user:
                raise ValueError("Usuário não existente❌")
            
            now = datetime.now()

            user_entity = UserEntity(
                id=str(id),
                name=name if name is not None else existing_user.name,
                last_name=last_name if last_name is not None else existing_user.last_name,
                email=email if email is not None else existing_user.email,
                password=existing_user.password,
                created_at=existing_user.created_at,
                updated_at=now
            )

            user = self.user_repository.update_user(user_entity)

            return user
    
    def delete_user_by_id(self, id: UUID):
        get_user_id = self.user_repository.get_by_id(id)

        if not get_user_id:
            return ValueError("Usuário não existente❌")
        
        user = self.user_repository.delete_user(id=id)

        return user
    
    def recovery_user_password(self, email: str, password:str) -> UserEntity:
        user_email = self.user_repository.get_by_email(email)

        #Depois deve ser feito o envio de email com o código de verificação

        if not user_email:
            raise ValueError("Usário ou e-mail não encontrado⚠️")
        
        new_password = make_password(password)

        user = self.user_repository.recover_password(email=email, password=new_password)

        return user
    
    def update_user_passsword(self, id:UUID, old_password:str, new_password: str) -> UserEntity:
        user_id = self.user_repository.get_by_id(id)

        if not user_id:
            raise ValueError("Usuário não existente❌")
        
        if not check_password(old_password, user_id.password):
            raise ValueError("Senha antiga incorreta🚫")
        
        #Enviar email ao usuário para notificar que a senha foi alterada

        user = self.user_repository.update_password(id, password=new_password)

        return user
        


        

        