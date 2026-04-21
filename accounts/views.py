from django.shortcuts import render

from rest_framework import generics
from .models import User
from .serializers import RegisterSerializer, UserSerializer


# Para registros, login y logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken


# Para permisos de roles
from .permissions import IsAdminUserRole 
from rest_framework.generics import ListAPIView

from rest_framework.generics import RetrieveUpdateAPIView
from .permissions import IsOwnerOrAdmin

# Para generar token seguro para restablecer contraseña
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

# Para restablecer contraseña
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

# Para listar usuarios (solo admin)
class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUserRole]

# Para ver perfil
class UserDetailView(RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrAdmin]



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
            token.blacklist()  # invalida el token con blaclist

            return Response({"message": "Logout exitoso"}, status=status.HTTP_205_RESET_CONTENT)

        except Exception:
            return Response({"error": "Token inválido"}, status=status.HTTP_400_BAD_REQUEST)    



# Generar token seguro para restablecer contraseña
token_generator = PasswordResetTokenGenerator()

class RequestPasswordResetView(APIView):
    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        uid = urlsafe_base64_encode(force_bytes(user.id)) # Codifica el ID del usuario
        token = token_generator.make_token(user) # Genera un token único para el usuario 

        reset_link = f"http://localhost:8000/api/reset-password/{uid}/{token}/" # Genera el enlace de restablecimiento

        return Response({
            "message": "Password reset link generated",
            "reset_link": reset_link
        })


# Restablecer contraseña
class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=uid)
        except:
            return Response({"error": "Invalid link"}, status=400)

        if not token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=400)

        new_password = request.data.get("new_password")
        user.set_password(new_password)
        user.save()

        return Response({"message": "Password reset successful"})