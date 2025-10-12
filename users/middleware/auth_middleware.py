from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from loguru import logger
from typing import Optional
from users.services.auth_service import AuthService
from users.helpers.errors.error import UnauthorizedError
from users.infra.userRepository import UserRepository
from jwt import InvalidTokenError, ExpiredSignatureError

class AuthMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.auth_service = AuthService(UserRepository())

    def process_request(self, request):
        token = None

        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()

        if not token:
            cookie_name = getattr(settings, "JWT_COOKIE_NAME", "access_token")
            token = request.COOKIES.get(cookie_name)
        
        if not token:
            request.user_id = None
            request.user = None
            return None
        
        try:
            payload = self.auth_service.decode_token(token=token)
            user_id = payload.get("sub")
            request.user_id = user_id

            if isinstance(user_id, str):
                try: 
                    request.user = self.auth_service.user_repository.get_by_id(user_id)
                except Exception:
                    request.user = None
            else:
                request.user = None
                
        except ExpiredSignatureError:
            logger.warning("Token expired, please do the login")
            request.user_id = None
            request.user = None
        
        except InvalidTokenError as e:
            logger.warning("Ivalid token: {}", e)
            request.user_id = None
            request.user = None
        
        except Exception as e:
            logger.exception("Error decoding token: {}", e)
            request.user_id = None
            request.user = None

        return None