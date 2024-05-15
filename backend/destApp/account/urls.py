from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView, UserLoginView, UserLogoutView, ListUserView,
    EditUserView)

urlpatterns = [
    path('register', UserRegistrationView.as_view(), name='register'),
    path('login', UserLoginView.as_view(), name='login'),
    path('logout', UserLogoutView.as_view(), name='logout'),
    # API token/refresh: pass refresh_token to body
    path('token/refresh', TokenRefreshView.as_view(), name='refresh-access-token'),
    path('users/', include([
        path('', ListUserView.as_view(), name='list-users'),
        path('<int:pk>', EditUserView.as_view(), name='edit-user'),
    ]))
]
