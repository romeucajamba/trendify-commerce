from users.domain.entities.user_entity import UserEntity
from users.domain.contracts.iuser_repository import IUserRepository
from users.models import User
from typing import Optional, List

class UserRepository(IUserRepository):

    def create(self, user: UserEntity) -> UserEntity:
        users = User.objects.create(
                name=user.name, 
                last_name=user.last_name, 
                email=user.email, 
                password=user.password
            )
        
        return UserEntity(
            id=str(users.id),
            name=users.name, 
            last_name=users.last_name,
            email=users.email, 
            password=users.password,
            created_at=users.created_at,
            updated_at=users.updated_at
        )

    def get_by_email(self, email: str) -> UserEntity | None:
        users = User.objects.filter(email=email).first()
        if not users:
            return None
        
        return UserEntity(
            id=str(users.id),
            name=users.name, 
            last_name=users.last_name,
            email=users.email, 
            password=users.password,
            created_at=users.created_at,
            updated_at=users.updated_at
        )
    
    def get_by_id(self, id:str) -> UserEntity | None:
        users = User.objects.filter(id=id).first()

        if not users:
            return None
        
        return UserEntity(
            id=str(users.id),
            name=users.name, 
            last_name=users.last_name,
            email=users.email, 
            password=users.password,
            created_at=users.created_at,
            updated_at=users.updated_at
        )

    def get_all_users(self) -> Optional[List[UserEntity]]:
        users = User.objects.all()

        return [UserEntity(
            id=str(user.id),
            name=user.name, 
            last_name=user.last_name,
            email=user.email, 
            password=user.password,
            created_at=user.created_at,
            updated_at=user.updated_at
            )
            for user in users
        ]

    def update_user(self, user:UserEntity) -> Optional[UserEntity]:
        try:
            db_user = User.objects.get(id=user.id)

        except User.DoesNotExist:
            return None
        
        db_user.name = user.name
        db_user.last_name = user.last_name
        db_user.email = user.email
        db_user.save()

        return UserEntity(
            id=str(db_user.id),
            name=db_user.name,
            last_name=db_user.last_name,
            email=db_user.email,
            password=db_user.password,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )

    def delete_user(self, id:str) -> None:
        
        user = User.objects.get(id=id)
        user.delete()

    def recover_password(self, email: str, password: str) -> Optional[UserEntity]:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        
        user.password=password
        user.save()

        return UserEntity(
            id=str(user.id),
            name=user.name,
            last_name=user.last_name,
            email=user.email,
            password=user.password,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    
    def update_password(self, id:str, password: str) -> Optional[UserEntity]:
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return None
        
        user.password=password
        user.save()

        return UserEntity(
            id=str(user.id),
            name=user.name,
            last_name=user.last_name,
            email=user.email,
            password=user.password,
            created_at=user.created_at,
            updated_at=user.updated_at
        )