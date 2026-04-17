from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

# Manager personalizado
class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El usuario debe tener un email")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # 🔐 encriptacion de la contraseña
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


# Modelo personalizado
class User(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'  # 👈 login con email
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email