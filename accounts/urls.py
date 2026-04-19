from accounts.views import UserDetailView
from accounts.views import UserListView
from django.urls import path
from .views import RegisterView, LoginView, ProfileView, LogoutView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('token/refresh', TokenRefreshView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('users/', UserListView.as_view()),
    path('users/<int:pk>/', UserDetailView.as_view()),
]