from django.urls import path
from . import views 

urlpatterns = [
    path('v1/users/', views.register_user, name="create_user")
]