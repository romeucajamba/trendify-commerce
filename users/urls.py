from django.urls import path
from .views import UserController, PasswordController, ConfirmAccountView, SpecificUserController

user_controller = UserController()
passwordController = PasswordController()
confirm_account = ConfirmAccountView()
user_id_controller = SpecificUserController()

urlpatterns = [
    path("register/", user_controller.as_view()),#post
    path("users/", user_controller.as_view()),#get
    path("users/<uuid:id>/", user_id_controller.as_view()),#get by id
    path("users/<uuid:id>/update/", user_controller.as_view()),#put
    path("users/<uuid:id>/delete/", user_controller.as_view()),#delte
    
    path("users/recovery-password/", passwordController.as_view()),
    path("users/<uuid:id>/update-password/", passwordController.as_view()),

    path("users/confirm-account/", ConfirmAccountView.as_view(), name="confirm-account"),
]