from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from .models import User
from .serializers import RegisterSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken





# Generar tokens
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# Registro
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)

            return Response({
                'user': UserSerializer(user).data,
                'tokens': tokens
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  


# Login
class LoginView(APIView):
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data
            tokens = get_tokens_for_user(user)

            return Response({
                'user': UserSerializer(user).data,
                'tokens': tokens
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Perfil
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)


# Logout
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # invalida el token con blacklist

            return Response({"message": "Logout exitoso"}, status=status.HTTP_205_RESET_CONTENT)

        except Exception:
            return Response({"error": "Token inválido"}, status=status.HTTP_400_BAD_REQUEST)    