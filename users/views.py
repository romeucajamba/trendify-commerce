from typing import Any, Dict, cast
from uuid import UUID
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from users.serializers import UserSerializer, PasswordUpdateSerializer, PasswordRecoverySerializer

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
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id: str):
        try:
            serializer = UserSerializer(data=request.data, partial=True)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            validated_data = cast(Dict[str, Any], serializer.validated_data)

            user = self.service.update_user_data(
                id,
                validated_data.get("name"),
                validated_data.get("last_name"),
                validated_data.get("email"),
            )

            if user is None:
                return Response({"error": "Usuário não encontrado"}, status=status.HTTP_404_NOT_FOUND)

            return Response(UserSerializer(user.__dict__).data, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request, id: str):
        try:
            self.service.delete_user_by_id(id)

            return Response(status=status.HTTP_204_NO_CONTENT)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class PasswordController(APIView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = UserService(UserRepository())

    def get(self, request, id: str): 
        try: 
            user = self.service.get_user_by_id(id) 
            if user is None:
                return Response({"error": "Usuário não encontrado"}, status=status.HTTP_404_NOT_FOUND)
            
            return Response({
            "id": str(user.id),
            "name": user.name,
            "last_name": user.last_name,
            "email": user.email,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = PasswordRecoverySerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            validated_data = cast(Dict[str, Any], serializer.validated_data)

            user = self.service.recovery_user_password(
                validated_data["email"],
                validated_data["password"],
            )
            if user is None:
                return Response({"error": "Usuário não encontrado"}, status=status.HTTP_404_NOT_FOUND)

            return Response(UserSerializer(user.__dict__).data, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id:str):
        try:
            serializer = PasswordUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            validated_data = cast(Dict[str, Any], serializer.validated_data)

            user = self.service.update_user_password(
                id,
                validated_data["old_password"],
                validated_data["new_password"],
            )
            if user is None:
                return Response({"error": "Usuário não encontrado"}, status=status.HTTP_404_NOT_FOUND)

            return Response(UserSerializer(user.__dict__).data, status=status.HTTP_200_OK)

        except ValueError as e:
            # ex: senha antiga incorreta
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
