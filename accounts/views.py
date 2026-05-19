from django.shortcuts import render

from rest_framework import generics
from .models import User
from .serializers import RegisterSerializer, UserSerializer


# Para registros, login y logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, TokenResponseSerializer, LogoutSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer, ChangePasswordSerializer, UpdateProfileSerializer, DeleteAccountSerializer
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

# Para enviar email
from django.core.mail import send_mail
from django.conf import settings

#para vistas publicas
from rest_framework.permissions import AllowAny

# Para throttling
from .throttles import LoginThrottle, RegisterThrottle

# Para documentacion swagger
from drf_spectacular.utils import extend_schema


# Para tokens de verificación de correo electrónico
from .tokens import email_verification_token
from django.contrib.auth import get_user_model


# -------------------------------------------------------------
# -------------------------------------------------------------


# Para listar usuarios (solo admin)
class UserListView(ListAPIView):                                                            # vista para listar usuarios     
    queryset = User.objects.all()                                                           # obtengo todos los usuarios     
    serializer_class = UserSerializer                                                       # serializo los usuarios       
    permission_classes = [IsAdminUserRole]                                                # solo admin puede ver usuarios  

# Para ver perfil
class UserDetailView(RetrieveUpdateAPIView):                                            # vista para ver perfil         
    queryset = User.objects.all()                                                           # obtengo todos los usuarios     
    serializer_class = UserSerializer                                                       # serializo los usuarios       
    permission_classes = [IsOwnerOrAdmin]                                               # solo el dueño o admin puede ver el perfil



# Generar tokens
def get_tokens_for_user(user):                                                          # funcion para generar tokens
    refresh = RefreshToken.for_user(user)                                                 # obtengo el refresh token      

    return {
        'refresh': str(refresh),                                                          # devuelvo el refresh token
        'access': str(refresh.access_token),                                              # devuelvo el access token
    }


# Registro
email_token_generator = PasswordResetTokenGenerator() # genera token de verificacion

@extend_schema(
    request=RegisterSerializer,                                                             # solicitud de registro
    responses=TokenResponseSerializer                                                       # respuesta exitosa
)
class RegisterView(APIView):                                                                # vista para registro         
    permission_classes = [AllowAny]                                                         # permite acceso sin autenticacion (token access)
    throttle_classes = [RegisterThrottle]                                                   # limita el numero de intentos de registro
    def post(self, request):                                                                # recibo el token de autenticacion
        serializer = RegisterSerializer(data=request.data)                                    # serializo los datos

        if serializer.is_valid():                                                          # valido que los datos sean validos
            user = serializer.save()                                                           # guardo el usuario
            
            
            #generar UID y token
            uid = urlsafe_base64_encode(force_bytes(user.id))                                   # codifico el id del usuario en uid
            token = email_token_generator.make_token(user)                                    # genero el token de verificacion

            verification_link = f"http://127.0.0.1:8000/api/verify-email/{uid}/{token}/"       # creo el link de verificacion

            send_mail(                                                                          # envio el correo de verificacion
                subject='Verifica tu cuenta',
                message=f'Haz clic aquí para verificar tu cuenta: {verification_link}',        # mensaje de verificacion
                from_email=settings.DEFAULT_FROM_EMAIL,                                     # correo del remitente
                recipient_list=[user.email],                                                    # correo del destinatario
                fail_silently=False,                                                            # silencio errores
            )
            return Response({
                "message": "Usuario creado. Por favor verifica tu correo electrónico.",       # mensaje de registro
                "verification_link": verification_link                                         # link de verificacion
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)            # respuesta si los datos no son validos

# Verificar email
class VerifyEmailView(APIView):                                                               # vista para verificar email
    permission_classes = [AllowAny]                                                         # permite acceso sin autenticacion (token access)
    def get(self, request, uidb64, token):                                                  # recibo el token de autenticacion
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))                                    # decodifico el id del usuario en uid
            user = User.objects.get(id=uid)                                                   # obtengo el usuario
        except:
            return Response({"error": "Enlace inválido"}, status=400)                         # respuesta si el enlace es invalido

        if not email_token_generator.check_token(user, token):                                # valido el token de verificacion
            return Response({"error": "Token inválido o expirado"}, status=400)               # respuesta si el token es invalido

        user.is_verified = True                                                             # marco el usuario como verificado
        user.save()                                                                         # guardo el usuario

        return Response({"message": "Correo electrónico verificado exitosamente"})          # respuesta exitosa


# Login
@extend_schema(
    request=LoginSerializer,                                                             # solicitud de login
    responses=TokenResponseSerializer                                                    # respuesta exitosa
)
class LoginView(APIView):                                                              # login
    permission_classes = [AllowAny]                                                        # permite acceso sin autenticacion (token access)
    throttle_classes = [LoginThrottle]                                                     # limita el numero de intentos de login

    def post(self, request):                                                             # recibo el token de autenticacion
        serializer = LoginSerializer(data=request.data)                                    # serializo los datos

        if serializer.is_valid():                                                          # valido que los datos sean validos
            user = serializer.validated_data                                               # obtengo los datos validados
            tokens = get_tokens_for_user(user)                                             # obtengo los tokens

            return Response({
                'user': UserSerializer(user).data,                                           # devuelvo el usuario
                'tokens': tokens                                                             # devuelvo los tokens
            }, status=status.HTTP_200_OK)                                                  # respuesta exitosa
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)         # respuesta de error



# Perfil
@extend_schema(
    responses=UserSerializer                                                              # respuesta exitosa
)
class ProfileView(APIView):  # perfil de usuario
    permission_classes = [IsAuthenticated]                                             # necesita autenticacion token

    def get(self, request):                                                            # recibo el token de autenticacion
        user = request.user                                                                # obtengo el usuario autenticado
        return Response({
            'user': UserSerializer(user).data                                           # devuelvo el usuario
        }, status=status.HTTP_200_OK)                                                  # respuesta exitosa


# Logout
@extend_schema(
    request=LogoutSerializer,                                                         # recibo el token de refresco
    responses={200: None}                                                             # respuesta exitosa
)
class LogoutView(APIView):  # cerrar sesion 
    permission_classes = [IsAuthenticated]                                             # necesita autenticacion token

    def post(self, request):                                                             # recibo el token de refresco
        try:
            refresh_token = request.data["refresh"]                                        # obtengo el token de refresco
            token = RefreshToken(refresh_token)
            token.blacklist()  # invalida el token con blaclist

            return Response({"message": "Logout exitoso"}, status=status.HTTP_200_OK)        # mensaje de confirmacion

        except Exception:
            return Response({"error": "Token inválido"}, status=status.HTTP_400_BAD_REQUEST)    # si el token es invalido



# Generar token seguro para restablecer contraseña
token_generator = PasswordResetTokenGenerator()  # genera token de verificacion para restablecer contraseña

@extend_schema(
    tags=["Authentication"],                                                                # etiqueta
    request=PasswordResetRequestSerializer,                                            # solicitud de email
    responses={
        200: {                                                                         # respuesta exitosa
            "type": "object",
            "properties": {
                "message": {
                    "type": "string"
                }
            }
        }
    }
)
class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]                                             # sin autenticacion
    def post(self, request):                                                    # recibo el email
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)                              # busco el usuario por email
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=404)   # si no existe el usuario lanzo error

        uid = urlsafe_base64_encode(force_bytes(user.id))                     # Codifica el ID del usuario
        token = token_generator.make_token(user)                              # Genera un token único para el usuario 

        reset_link = f"http://localhost:8000/api/reset-password/{uid}/{token}/" # Genera el enlace de restablecimiento

        return Response({
            "message": "Enlace de restablecimiento de contraseña generado",    # mensaje de confirmacion
            "reset_link": reset_link                                            # enlace de restablecimiento
        }, status=status.HTTP_200_OK)                                          # devuelvo un mensaje con estatus 200 ok


# Restablecer contraseña
@extend_schema(                                                             # es una libreria para documentar la API con drf spectacular
    tags=["Authentication"],                                                # en que categoria se encuentra la API
    request=PasswordResetConfirmSerializer,                                   # que tipo de datos espero recibir
    responses={
        200: {                                                              # respuesta exitosa
            "type": "object",
            "properties": {
                "message": {
                    "type": "string"
                }
            }
        }
    }
)
class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]                                             # sin autenticacion
    def post(self, request, uidb64, token):                                       #  recibo el id y el token decodificados
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))                        # decodifico el id
            user = User.objects.get(id=uid)                                     # obtengo el usuario
        except:                                                                   # si no existe el usuario lanzo error
            return Response({"error": "Enlace inválido"}, status=400)

        if not token_generator.check_token(user, token):                        # si el token es invalido lanzo error
            return Response({"error": "Enlace inválido o expirado"}, status=400)

        new_password = request.data.get("new_password")                         # obtengo la nueva contraseña
        user.set_password(new_password)                                         # establezco la nueva contraseña
        user.save()                                                             # guardo el perfil

        return Response({"message": "Contraseña restablecida correctamente"}, status=status.HTTP_200_OK)  # devuelvo un mensaje con estatus 200 ok 


# cambiar contraseña de un usuario autenticado 
# con old_password y new_password
class ChangePasswordView(APIView):                          

    permission_classes = [IsAuthenticated]                 # necesario autenticacion para poder cambiar la contraseña

    serializer_class = ChangePasswordSerializer            # le paso el serializer para usarlo en el metodo post

    def post(self, request):                          

        serializer = ChangePasswordSerializer(             # inicializo el serializer
            data=request.data                              # le paso los datos del request
        )

        serializer.is_valid(raise_exception=True)          # si es valido lanzo error con raise_exception=True

        user = request.user                                # obtengo el usuario autenticado

        old_password = serializer.validated_data[
            'old_password'                                   # obtengo la contraseña vieja
        ]

        new_password = serializer.validated_data[
            'new_password'                                   # obtengo la contraseña nueva
        ]

        if not user.check_password(old_password):            # si la contraseña vieja es incorrecta lanzo error

            return Response({
                "error": "Contraseña incorrecta"
            }, status=status.HTTP_400_BAD_REQUEST)          # status 400 bad request

        user.set_password(new_password)                      # establezco la nueva contraseña

        user.save()                                          # guardo el perfil

        return Response({                                     # devuelvo un mensaje con estatus 200 ok 
            "message": "Contraseña actualizada correctamente"
        }, status=status.HTTP_200_OK)


# actualizar perfil de un usuario autenticado 
class UpdateProfileView(APIView):

    permission_classes = [IsAuthenticated]   # necesario autenticacion para poder actualizar el perfil 

    serializer_class = UpdateProfileSerializer   # le paso el serializer para usarlo en el metodo put

    def put(self, request):

        serializer = UpdateProfileSerializer(      # inicializo el serializer 
            request.user,                          # le paso el usuario autenticado
            data=request.data,                     # le paso los datos del request
            partial=True                           # le paso partial=True para que pueda actualizar solo algunos campos 
        )

        if serializer.is_valid():                  # si es valido lanzo error con raise_exception=True 

            serializer.save()                      # si es valido guardo el perfil

            return Response({                      # y devuelvo un mensaje 
                "message": "Perfil actualizado correctamente",
                "data": serializer.data                # los campos actualizados
            }, status=status.HTTP_200_OK)        # status 200 ok  

        return Response(
            serializer.errors,                     # si no es valido lanzo error con raise_exception=True
            status=status.HTTP_400_BAD_REQUEST   # status 400 bad request
        )

# eliminar cuenta de usuario autenticado
class DeleteAccountView(APIView):

    permission_classes = [IsAuthenticated]      # necesario autenticacion para poder eliminar la cuenta

    serializer_class = DeleteAccountSerializer  # le paso el serializer para usarlo en el metodo post

    def post(self, request):

        serializer = DeleteAccountSerializer( # le paso la contraseña del usuario
            data=request.data                   # validando si es correcta
        )

        serializer.is_valid(                   # si es correcta lanza error con raise_exception=True
            raise_exception=True
        )

        password = serializer.validated_data[ # si es correcta la guardo 
            'password'
        ]

        user = request.user

        if not user.check_password(password): # si no es correcta lanza error

            return Response({
                "error": "Contraseña incorrecta" # mensaje de error
            }, status=status.HTTP_400_BAD_REQUEST) # status 400 bad request

        user.delete() # elimina la cuenta

        return Response({                     # y devuelve un mensaje con status 200
            "message": "Cuenta eliminada correctamente"
        }, status=status.HTTP_200_OK)