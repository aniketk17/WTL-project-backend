from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("user-profile-details/", UserProfileDetailsView.as_view(), name="user_profile_details"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
