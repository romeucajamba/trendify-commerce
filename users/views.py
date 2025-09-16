from typing import Any
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from uuid import UUID
from users.services.user_service import UserService
from users.infra.userRepository import UserRepository
# Create your views here.

class UserController(APIView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = UserService(UserRepository())

    def register_user(self, request):
        try:
            name = request.data.get("name")
            last_name = request.data.get("last_name")
            email = request.data.get("email")
            password = request.data.get("password")
            confirm_password = request.data.get("confirm_password")

            if not all([name, last_name, email, password, confirm_password]):
                
                return Response(
                    {"error":"Todos os campos são obrigatórios⚠️"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user = self.service.create_user(name, last_name, email, password)

            return Response(user.__dict__, status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        
        except Exception as e:
            return Response({"error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_users(self):
        try:

            users = self.service.get_all_users()

            if not users:
                return []
            
            return Response([user.__dict__ for user in users], status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error":str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_user_by_id(self, id: str):
        try:
            user = self.service.get_user_by_id(id=UUID(id))

            return Response(
                user.__dict__,
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response({"error": str(e)},
                            status=status.HTTP_404_NOT_FOUND
                            )
        except Exception as e:
            return Response(
                {"error":str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update_same_user_data(self, id: str, request):
        try:
            name = request.data.get("name")
            last_name = request.data.get("last_name")
            email = request.data.get("email")

            user = self.service.update_user_data(
                UUID(id),
                name,
                last_name,
                email
            )

            return Response(user.__dict__, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    def delete_user_id(self, id: str, request):
        try:
            self.service.delete_user_by_id(UUID(id))

            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    def recuvery_password(self, request):
        try:
            email = request.data.get("email")
            password = request.data.get("password")
            confirm_password = request.data.get("confirm_password")

            if not email or not password or not confirm_password:
                return Response(
                    {"error": "Todos os campos são obrigatórios⚠️"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user = self.service.recovery_user_password(email, password)

            return Response(
                user.__dict__,
                status=status.HTTP_200_OK
            )
       
        except ValueError as e:
            return Response(
                {"error":str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    def update_password(self, request, id: str):
        try:
            old_password = request.data.get("old_password")
            new_password = request.data.get("new_password")
            confirm_password = request.data.get("confirm_password")

            if not old_password or not new_password or not confirm_password:
                return Response(
                    {"error": "Todos os campos são obrigatórios⚠️"}
                )
            
            user = self.service.update_user_passsword(
                    UUID(id),
                    old_password,
                    new_password
                )
            
            return Response(
                user.__dict__,
                status=status.HTTP_200_OK
            )
        
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )