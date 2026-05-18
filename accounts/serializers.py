from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user
    
# Logueo
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        # valida la password
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password")

        # bloquear si no esta veificada la cuenta con email
        if not user.is_verified:
            raise serializers.ValidationError("Email not verified")

        # valida si el usuario esta activo
        if not user.is_active:
            raise serializers.ValidationError("User is inactive")
        
        return user
    
#Perfil
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'created_at']


#tokens
class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

#logout
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

#resetear contraseña
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


#confirmar reset de contraseña
class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):

        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                "Passwords do not match"
            )

        return data

# para cambiar contraseña del usuario (actual y nueva)
class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(
        write_only=True
    )

    new_password = serializers.CharField(
        write_only=True,
        min_length=8
    )



# actualizar perfil (email y username) del usuario autenticado
class UpdateProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'email']


# para eliminar la cuenta, pedir la contraseña para verificar que es el usuario
class DeleteAccountSerializer(serializers.Serializer):

    password = serializers.CharField(
        write_only=True
    )