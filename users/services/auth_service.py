import jwt
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from django.conf import settings
from users.domain.contracts.iuser_repository import IUserRepository
from users.domain.entities.user_entity import UserEntity
from django.contrib.auth.hashers import check_password

class AuthService:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    def autheticate(self, email:str, password: str) -> UserEntity | None:
        user = self.user_repository.get_by_email(email=email)

        if not user:
            return None
        if not check_password(password, user.password):
            return None
        
        return user
    
    def create_access_token(self, user_id: str) -> str:
        now = datetime.utcnow()

        payload: Dict[str, Any] = {
            "sub": str(user_id),
            "iat": now,
            "exp": now + timedelta(seconds=settings.JWT_EXP_SECONDS),
            "jti": str(uuid.uuid4()),
            "iss": getattr(settings, "JWT_ISSUER", "trendify-e-commerce")
        }

        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        return token
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM], issuer=getattr(settings, "JWT_ISSUER", None))

        return payload