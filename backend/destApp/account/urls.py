from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserRegistrationView, UserLoginView, UserLogoutView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    # API token/refresh: pass refresh_token to body
    path('token/refresh', TokenRefreshView.as_view(), name='refresh_access_token')
]
