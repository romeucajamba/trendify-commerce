from typing import Any, Dict, cast
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.serializers import UserSerializer, PasswordUpdateSerializer, PasswordRecoverySerializer, ConfirmAccountSerializer, UserUpadateDataSerializer
from users.helpers.errors.error import BadRequestError, ConflictError, NotFoundError, UnauthorizedError, DatabaseError,AppError

from users.services.user_service import UserService
from users.infra.userRepository import UserRepository

class UserController(APIView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = UserService(UserRepository())

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

    def put(self, request, id: str):
        try:
            if id == None:
                raise UnauthorizedError(safe_message="Not authorized to proceed with the operation", status_code=401, code="unauthorized")
            
                user_id = self.service.get_user_by_id(id)

                if user_id is None:
                    raise NotFoundError(safe_message="User not found", status_code=404, code="not_found")
            
            serializer = UserUpadateDataSerializer(data=request.data, partial=True)

            if not serializer.is_valid():
                raise BadRequestError(safe_message="invalid data", status_code=400, code="bad_request", extra=serializer.errors)

            validated_data = cast(Dict[str, Any], serializer.validated_data)

            user = self.service.update_user_data(
                id,
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
        
    def delete(self, request, id: str):
        try:
            if not id:
                raise UnauthorizedError(safe_message="Not authorized to proceed with the operation", status_code=401, code="unauthorized")

            userId = self.service.delete_user_by_id(id)

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

class SpecificUserController(APIView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = UserService(UserRepository())

    def get(self, request, id: str): 
        try: 
            if not id:
                raise UnauthorizedError(safe_message="Not authorized to proceed with the operation", status_code=401, code="unauthorized")
            
            user = self.service.get_user_by_id(id) 

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

class PasswordController(APIView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = UserService(UserRepository())

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

    def put(self, request, id:str):
        try:
            if not id:
                raise UnauthorizedError(safe_message="Not authorized to proceed with the operation", status_code=401, code="unauthorized")
            
            serializer = PasswordUpdateSerializer(data=request.data)

            if not serializer.is_valid():
                raise BadRequestError(safe_message="invalid data",status_code=400, code="bad_request", extra=serializer.errors)

            validated_data = cast(Dict[str, Any], serializer.validated_data)

            user = self.service.update_user_password(
                id,
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
