from django.urls import path
from .views import RegisterView, LoginView, ProfileView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('token/refresh', TokenRefreshView.as_view()),
]