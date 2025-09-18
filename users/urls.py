from django.urls import path
from .views import UserController, PasswordController

user_controller = UserController()
passwordController = PasswordController()

urlpatterns = [
    path("register/", user_controller.as_view()),
    path("users/", user_controller.as_view()),
    path("users/<uuid:id>/", passwordController.as_view()),
    path("users/<uuid:id>/update/", user_controller.as_view()),
    path("users/<uuid:id>/delete/", user_controller.as_view()),
    
    path("users/recovery-password/", passwordController.as_view()),
    path("users/<uuid:id>/update-password/", passwordController.as_view()),
]