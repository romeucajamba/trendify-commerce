from typing import Any, Dict, cast
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from users.serializers import UserSerializer, PasswordUpdateSerializer, PasswordRecoverySerializer, ConfirmAccountSerializer, UserUpadateDataSerializer
from users.helpers.logs.logger import logger
from users.helpers.errors.error import BadRequestError, ConflictError, NotFoundError, UnauthorizedError, DatabaseError,AppError
from django.conf import settings
from users.services.user_service import UserService
from users.services.auth_service import AuthService
from users.infra.userRepository import UserRepository

class AuthenticatedAPIView(APIView):
    def dispatch(self, request, *args, **kwargs):
        if getattr(request, "user_id", None) is None:
            raise UnauthorizedError(safe_message="Autentication required", status_code=401, code="unauthorized")
        return super().dispatch(request, *args, **kwargs)
        
class LoginView(APIView):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.auth_service = AuthService(UserRepository())

    @swagger_auto_schema(
        operation_description="User login and JWT token generation",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, format="email"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, format="password"),
            },
        ),
        responses={
            202: openapi.Response(
                description="Successful login",
                examples={
                    "application/json": {
                        "access_token": "jwt_token_here",
                        "token_type": "bearer",
                        "user": {
                            "id": "uuid",
                            "name": "Romeu",
                            "last_name": "Cajamba",
                            "email": "example@gmail.com"
                        }
                    }
                },
            ),
            400: "E-mail or password not provided",
            401: "Invalid credentials",
        },
    )    

    def post(self, request):
        data = request.data
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            raise BadRequestError(safe_message="E-mail and password are required", status_code=400, code="bad_request")
        
        user = self.auth_service.autheticate(email=email, password=password)

        if not user:
            raise UnauthorizedError(safe_message="Invalid credentials", status_code=401, code="unathorized")
        
        token = self.auth_service.create_access_token(user.id)

        #define cookie HttOnly + returna token
        response = Response({
            "access_token": token,
            "token_type": "bearer",
            "user": UserSerializer(user.__dict__).data
        }, status=status.HTTP_202_ACCEPTED)

        cookie_name = getattr(settings, "JWT_COOKIE_NAME", "access_token")

        response.set_cookie(
            cookie_name,
            token,
            httponly=True,
            secure=getattr(settings, "JWT_COOKIE_SECURE", False),
            samesite=getattr(settings, "JWT_COOKIE_SAMESITE", "Lax"),
            max_age=getattr(settings, "JWT_EXP_SECONDS", 3600)
        )

        logger.info("User logged in: {}", user.email)

        return response
    
class LogoutView(APIView):
    @swagger_auto_schema(
            operation_description="Logs out the user by deleting the JWT token from cookies.",
            responses={
                200: openapi.Response(
                    description="Sucessful logout",
                    examples={
                        "application/json":{
                            "message": "Logged out"
                        }
                    }
                ),
                401: "User not autenticated or already logged out"
            },
            tags=["Authentication"]
    )
    
    def post(self, request):
        #AO fazer o loggout ele limpa os cookie
        response = Response({"message": "Logged out"}, status=status.HTTP_200_OK)

        cookie_name = getattr(settings, "JWT_COOKIE_NAME", "access_token")

        response.delete_cookie(cookie_name)

        return response

class UserSignUpView(APIView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = UserService(UserRepository())
    
    @swagger_auto_schema(
            operation_description="Register a new user in the system",
            request_body=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=["name", "last_name", "email", "password", "confirm_password"],
                properties={
                    "name":openapi.Schema(type=openapi.TYPE_STRING, example="Romeu"),
                    "last_name": openapi.Schema(type=openapi.TYPE_STRING, example="Cajamba"),
                    "email": openapi.Schema(type=openapi.TYPE_STRING, format="email", example="example@gmail.com"),
                    "password": openapi.Schema(type=openapi.TYPE_STRING, format="password", example="strongP@ssword122&"),
                    "confirm_password": openapi.Schema(type=openapi.TYPE_STRING, format="password", example="strongP@ssword122&")
                },
            ),
            responses={
                201: openapi.Response(
                    description="User sucessfully registered!",
                    examples={
                        "application/json":{
                            "id": "uuid",
                            "name": "Romeu",
                            "last_name": "Cajamba",
                            "email": "example@gmail.com"
                        },
                    },
                ),
                400: "Inavlid input data",
                409:"E-mail or user already exists",
                500: "Internal server error",
            },
            tags=["Authentication"]
    )

    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)

            # valida e retorna 400 com erros do serializer se inválido
            if not serializer.is_valid():
                raise BadRequestError(safe_message="Invalid data", status_code=400, extra=serializer.errors, code="bad_request")

            # informa ao type checker que validated_data é dict
            validated_data = cast(Dict[str, Any], serializer.validated_data)

            user = self.service.create_user(
                validated_data["name"],
                validated_data["last_name"],
                validated_data["email"],
                validated_data["password"],
            )

            return Response(UserSerializer(user.__dict__).data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            # Erro de regra de negócio (ex.: email duplicado)
            raise ConflictError(safe_message="E-mail or user alrady exists", status_code=409, code="conflict")
        except AppError:
            # deixa o middleware global tratar os AppError customizados
            raise
        except Exception as e:
            raise DatabaseError(safe_message="Something went wrong on our side, please try again later, and if it persists, contact us", status_code=500, code="internal_server_error")


class UserView(AuthenticatedAPIView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = UserService(UserRepository())
    
    @swagger_auto_schema(
            operation_description="Retrieve a list of all registered users (requires authentication).",
            responses={
                200: openapi.Response(
                    description="List o users retrieved sucessfully",
                    examples=
                    {
                        "application/json":[
                            {
                                "id": "uuid",
                                "name": "Romeu",
                                "last_name": "Cajamba",
                                "email": "example@gmail.com"
                            },
                        ],
                    },
                ),
            401: "Unauthorized acess",
            500: "Internal server error",
        },
        tags=["User Management"]
    )
    def get(self, request):
        try:

            users = self.service.get_all_users()
            if not users:
                return Response([], status=status.HTTP_200_OK)

            return Response(
                [UserSerializer(user.__dict__).data for user in users],
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            raise DatabaseError(safe_message="Something went wrong on our side, please try again later, and if it persists, contact us", status_code=500, code="internal_server_error")
        
    @swagger_auto_schema(
            operation_description="Update the authenticated user's profile",
            request_body=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "name": openapi.Schema(type=openapi.TYPE_STRING, example="Romeu"),
                    "last_name": openapi.Schema(type=openapi.TYPE_STRING, example="Cajamba"),
                    "email": openapi.Schema(type=openapi.TYPE_STRING, format="email", example="romeucajambaexample@gmail.com")
                }
            ),
            responses={
                200: openapi.Response(
                    description="User data sucessfully updated",
                    examples={
                        "application/json":{
                            "id": "uuid",
                            "name": "Romeu",
                            "last_name": "Cajamba",
                            "email": "reomeuexample12@gmail.com"
                        },
                    },
                ),
                400: "Invalid data provided",
                401: "Unautorized acess",
                404: "User not found",
                500: "Internal server error"
            },
            tags=["User Management"],
    )

    def put(self, request):
        try:
            take_user_auth_by_id = request.user_id

            if take_user_auth_by_id == None:
                raise UnauthorizedError(safe_message="Not authorized to proceed with the operation", status_code=401, code="unauthorized")
            
            user_by_id = self.service.get_user_by_id(take_user_auth_by_id)

            if user_by_id is None:
                raise NotFoundError(safe_message="User not found", status_code=404, code="not_found")
            
            serializer = UserUpadateDataSerializer(data=request.data, partial=True)

            if not serializer.is_valid():
                raise BadRequestError(safe_message="invalid data", status_code=400, code="bad_request", extra=serializer.errors)

            validated_data = cast(Dict[str, Any], serializer.validated_data)

            user = self.service.update_user_data(
                take_user_auth_by_id,
                validated_data.get("name"),
                validated_data.get("last_name"),
                validated_data.get("email"),
            )

            if not user:
                raise NotFoundError(safe_message="User not found", status_code=404, code="not_found")

            return Response(UserSerializer(user.__dict__).data, status=status.HTTP_200_OK)

        except ValueError as e:
            raise BadRequestError(safe_message="Something unexpected happened", status_code=400, code="bad_request")
        except AppError:
            # deixa o middleware global tratar os AppError customizados
            raise
        except Exception as e:
            raise DatabaseError(safe_message="Something went wrong on our side, please try again later, and if it persists, contact us", status_code=500, code="internal_server_error")
    
    @swagger_auto_schema(
            operation_description="Delete the a user account",
            responses={
                204: openapi.Response(description="User deleted sucessfully"),
                401: "Unauthorized acess",
                404: "User not found",
                500: "Internal server error"
            },
            tags=["User Management"]
    )
        
    def delete(self, request):
        try:
            take_user_auth_by_id = request.user_id

            if not take_user_auth_by_id:
                raise UnauthorizedError(safe_message="Not authorized to proceed with the operation", status_code=401, code="unauthorized")

            userId = self.service.delete_user_by_id(take_user_auth_by_id)

            if not userId:
                raise NotFoundError(safe_message="user not found", status_code=404, code="not_found")

            return Response(status=status.HTTP_204_NO_CONTENT)

        except ValueError as e:
            raise BadRequestError(safe_message="Something unexpected happened", status_code=400, code="bad_request")
        except AppError:
            # deixa o middleware global tratar os AppError customizados
            raise
        except Exception as e:
            raise DatabaseError(safe_message="Something went wrong on our side, please try again later, and if it persists, contact us", status_code=500, code="internal_server_error")

class UserProfileView(AuthenticatedAPIView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = UserService(UserRepository())

    @swagger_auto_schema(
        operation_description="Retrieve the authenticated user's profile (requires authentication)",
        responses={
            200: openapi.Response(
                description="Successfully retrieved user profile",
                examples={
                    "application/json":{
                        "id": "uuid",
                        "name": "Romeu",
                        "last_name": "Cajamba",
                        "email": "romeuexample@gmail.com",
                        "created_at": "2025-12-12T10:00:00Z",
                        "updated_at": "2025-12-12T10:00:00Z"
                    },
                },
            ),
            401: "Unauthorized acess",
            404: "User not found",
            500: "Internal server error",
        },
        tags=["User Management"],
    )

    def get(self, request): 
        try: 
            user_auth_by_id = request.user_id

            if not user_auth_by_id:
                raise UnauthorizedError(safe_message="Not authorized to proceed with the operation", status_code=401, code="unauthorized")
            
            user = self.service.get_user_by_id(user_auth_by_id) 

            if not user :
                raise NotFoundError(safe_message="User not found", status_code=404, code="not_found")
            
            return Response({
            "id": str(user.id),
            "name": user.name,
            "last_name": user.last_name,
            "email": user.email,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        }, status=status.HTTP_200_OK)
        
        except AppError:
            # deixa o middleware global tratar os AppError customizados
            raise
        except Exception as e:
            raise DatabaseError(safe_message="Something went wrong on our side, please try again later, and if it persists, contact us", status_code=500, code="internal_server_error")

class RecoveryPasswordView(APIView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = UserService(UserRepository())
    
    @swagger_auto_schema(
        operation_description="Allows a user to reset their password using registered email",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password", "confirm_password"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, format="email", description="The user's registered email address"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, format="password", description="The new password to set for the user account"),
                "confirm_password": openapi.Schema(type=openapi.TYPE_STRING, format="confirm_password", description="The same password"),
            },
        ),
        responses={
            200: openapi.Response(
                description="Password sucessfully updated",
                examples={
                    "application/json":{
                        "id": "uuid",
                        "name": "Romeu",
                        "last_name": "Cajamba",
                        "email": "romeuexample@gmail.com",
                        "created_at": "2025-10-06T10:00:00Z",
                        "updated_at": "2025-10-06T10:10:00Z"
                    },
                },
            ),
            400: "Ivalid input data",
            404: "User not found",
            500: "Internal server error"
        },
        tags=["Authentication"]
    )

    def post(self, request):
        try:
            serializer = PasswordRecoverySerializer(data=request.data)

            if not serializer.is_valid():
                raise BadRequestError(safe_message="Invalid data", status_code=400, code="bad_request", extra=serializer.errors)

            validated_data = cast(Dict[str, Any], serializer.validated_data)

            user = self.service.recovery_user_password(
                validated_data["email"],
                validated_data["password"],
            )

            if user is None:
                raise NotFoundError(safe_message="user not found", status_code=404, code="not_found")

            return Response(UserSerializer(user.__dict__).data, status=status.HTTP_200_OK)

        except AppError:
            # deixa o middleware global tratar os AppError customizados
            raise
        except Exception as e:
            raise DatabaseError(safe_message="Something went wrong on our side, please try again later, and if it persists, contact us", status_code=500, code="internal_server_error")

class PasswordView(AuthenticatedAPIView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = UserService(UserRepository())

    @swagger_auto_schema(
        operation_description="Allows an authenticated user to update their password by providing the current password and a new one.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["old_password", "new_password", "confirm_password"],
            properties={
                "old_password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format="password",
                    description="The user's current password."
                ),
                "new_password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format="password",
                    description="The new password the user wants to set."
                ),
                  "confirm_password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format="password",
                    description="The new password the user wants to set."
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Password successfully updated.",
                examples={
                    "application/json": {
                        "id": "uuid",
                        "name": "Romeu",
                        "last_name": "Cajamba",
                        "email": "romeu@example.com",
                        "created_at": "2025-10-06T10:00:00Z",
                        "updated_at": "2025-10-06T10:20:00Z"
                    }
                },
            ),
            400: "Invalid input data.",
            401: "Unauthorized access. Token missing or invalid.",
            404: "User not found.",
            500: "Internal server error.",
        },
        tags=["Authentication"],
    )

    def put(self, request):
        try:
            user_auth_by_id = request.user_id

            if not user_auth_by_id:
                raise UnauthorizedError(safe_message="Not authorized to proceed with the operation", status_code=401, code="unauthorized")
            
            serializer = PasswordUpdateSerializer(data=request.data)

            if not serializer.is_valid():
                raise BadRequestError(safe_message="invalid data",status_code=400, code="bad_request", extra=serializer.errors)

            validated_data = cast(Dict[str, Any], serializer.validated_data)

            user = self.service.update_user_password(
                user_auth_by_id,
                validated_data["old_password"],
                validated_data["new_password"],
            )

            if user is None:
                raise NotFoundError(safe_message="user not found", status_code=404, code="not_found")

            return Response(UserSerializer(user.__dict__).data, status=status.HTTP_200_OK)

        except AppError:
            # deixa o middleware global tratar os AppError customizados
            raise
        except Exception as e:
            raise DatabaseError(safe_message="Something went wrong on our side, please try again later, and if it persists, contact us", status_code=500, code="internal_server_error")

class ConfirmAccountView(APIView):

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = UserService(UserRepository())

    @swagger_auto_schema(
        operation_description="Confirm a user account using a verification code sent via email",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "code"],
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format="email",
                    description="The email address used to register the account"
                ),
                "code": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    maxLength=6,
                    description="The 6-digit verification code sent to the user's email"
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Account sucessfully confirmed",
                examples={
                    "application/json":{
                        "message": "Account sucessfully confirmed"
                    },
                },
            ),
            400: "Ivalid input data",
            404: "User not found or invalid confirm code",
            500: "Internal server error"
        },
        tags=["Authentication"]
    )

    def post(self, request):
        serializer = ConfirmAccountSerializer(data=request.data)

        if not serializer.is_valid():
            raise BadRequestError(safe_message="invalid data", status_code=400, code="bad_request", extra=serializer.errors)
        
        validated_data = cast(Dict[str, Any], serializer.validated_data)

        email = validated_data["email"]
        code = validated_data["code"]

        try:
            user = self.service.confirm_user(email, code)

            if user is None:
                raise NotFoundError(safe_message="user not found", status_code=404, code="not_found")

            return Response({"message": "Account successfully confirmed 🎉"}, status=status.HTTP_200_OK)
        
        except AppError:
            # deixa o middleware global tratar os AppError customizados
            raise
        except Exception as e:
            raise DatabaseError(safe_message="Something went wrong on our side, please try again later, and if it persists, contact us", status_code=500, code="internal_server_error")