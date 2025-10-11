from django.urls import path
from .views import LoginView, ConfirmAccountView, PasswordView, UserProfileView, UserView, LogoutView, UserSignUpView, RecoveryPasswordView

user_controller = UserView()
passwordController = PasswordView()
confirm_account = ConfirmAccountView()
user_profile_controller = UserProfileView()
user_login_controller = LoginView()
user_logout_controller = LogoutView()
signup = UserSignUpView()
recoveryPasswordController = RecoveryPasswordView()

urlpatterns = [
    path("login/", user_login_controller.as_view(), name="login"),#post
    path("logout/", user_logout_controller.as_view(), name="logout"),#post
    path("register/", signup.as_view(), name="create-account"),#post
    path("users/", user_controller.as_view(), name="get-all-users"),#get
    path("users/me/", user_profile_controller.as_view(), name="get-user"),#get by id
    path("users/update/", user_controller.as_view(), name="update-user-data"),#put
    path("users/delete/", user_controller.as_view(), name="delete-account"),#delte
    
    path("users/recovery-password/", recoveryPasswordController.as_view(), name="recovery-password"),
    path("users/update-password/", passwordController.as_view(), name="update-password"),

    path("users/confirm-account/", ConfirmAccountView.as_view(), name="confirm-account"),
]