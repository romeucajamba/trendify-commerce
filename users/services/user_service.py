from users.services.mail_service import send_email_changed_password, send_email_code_confirmation
from typing import List, Optional
from datetime import datetime
from django.contrib.auth.hashers import make_password, check_password
from users.domain.contracts.iuser_repository import IUserRepository
from users.domain.entities.user_entity import UserEntity
import random
from datetime import timedelta
from  django.utils import timezone


class UserService:
    def __init__(self, user_repository:IUserRepository):
        self.user_repository =user_repository
    
    def create_user(self, name: str, last_name: str, email: str, password: str):
        
        now = datetime.now()
        code_confirmation = str(random.randint(100000, 999999))

        user_entity = UserEntity(
            id="",
            name=name,
            last_name=last_name,
            email=email,
            password=make_password(password),
            created_at=now,
            updated_at=now,
            is_active=False,
            confirmation_code=code_confirmation,
            confirmation_expires_at=now + timedelta(minutes=10)
        )
        
        get_user_by_email = self.user_repository.get_by_email(email=email)

        if get_user_by_email:
            raise ValueError("Já existe um usuário com esse email🚫")
        
        #Depois deve ser feito o envio de email para confirmar ao usuário o seu cadastro
        send_email_code_confirmation(
            assunto="🎉 Bem-vindo à Trendify Commerce!",
            nome=name,
            email_destino=email,
            mensagem="Obrigado por se cadastrar! Aproveite todos os recursos da plataforma 🚀",
            code=code_confirmation
        )
        
        user = self.user_repository.create(user_entity)

        return user
    
    def get_user_by_id(self, id: str)-> Optional[UserEntity]:
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
            id: str, 
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
                updated_at=now,
                is_active=existing_user.is_active,
                confirmation_code=existing_user.confirmation_code,
                confirmation_expires_at=existing_user.confirmation_expires_at
            )

            user = self.user_repository.update_user(user_entity)

            return user
    
    def delete_user_by_id(self, id: str):
        get_user_id = self.user_repository.get_by_id(id)

        if not get_user_id:
            return ValueError("Usuário não existente❌")
        
        user = self.user_repository.delete_user(id=id)

        return user
    
    def recovery_user_password(self, email: str, password:str) -> UserEntity:
        user_email = self.user_repository.get_by_email(email=email)

        if not user_email:
            raise ValueError("Usário ou e-mail não encontrado⚠️")
        
        new_password = make_password(password)

        user = self.user_repository.recover_password(email=email, password=new_password)

        send_email_changed_password(
            assunto="🔑 Senha alterada com sucesso",
            nome=user.name,
            email_destino=user.email,
            mensagem="Sua senha foi alterada recentemente. Se não foi você, entre em contato imediatamente."
        )

        return user
    
    def update_user_password(self, id:str, old_password:str, new_password: str) -> UserEntity:
        user_id = self.user_repository.get_by_id(id)

        if not user_id:
            raise ValueError("Usuário não existente❌")
        
        if not check_password(old_password, user_id.password):
            raise ValueError("Senha antiga incorreta🚫")
        
        hashed_password = make_password(new_password)

        user = self.user_repository.update_password(id, password=hashed_password)

        send_email_changed_password(
            assunto="🔑 Senha alterada com sucesso",
            nome=user.name,
            email_destino=user.email,
            mensagem="Sua senha foi alterada recentemente. Se não foi você, entre em contato imediatamente."
        )

        return user
    
    def confirm_user(self, email: str, code: str):
        user = self.user_repository.get_by_email(email=email)

        if not user:
            raise ValueError("Usuário não encontrado 🚫")

        if user.is_active:
            raise ValueError("Usuário já está ativo ✅")

        if user.confirmation_code != str(code):
            raise ValueError("Código inválido 🚫")

        if  user.confirmation_expires_at < timezone.now():
            raise ValueError("Código expirado ⏰")

        # Ativar conta e invalidar código
        return self.user_repository.activate_user(email=user.email)