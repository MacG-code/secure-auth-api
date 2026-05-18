from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str

# Generador de tokens de verificación de correo electrónico basados en:
# - ID del usuario
# - Tiempo
# - Estado de verificación
class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) +
            str(timestamp) +
            str(user.is_verified)
        )


email_verification_token = EmailVerificationTokenGenerator()