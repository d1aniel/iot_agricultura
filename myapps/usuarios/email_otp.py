import secrets

from django.conf import settings
from django.core.mail import send_mail

from myapps.usuarios.models import LoginChallenge


def generar_codigo_otp():
    return f'{secrets.randbelow(1000000):06d}'


def enviar_codigo_otp_email(usuario, request=None, proposito='LOGIN', direccion_ip=None, user_agent=None):
    codigo = generar_codigo_otp()
    challenge = LoginChallenge.crear(
        usuario=usuario,
        codigo=codigo,
        direccion_ip=direccion_ip,
        user_agent=user_agent,
        proposito=proposito,
    )
    minutos = getattr(settings, 'EMAIL_OTP_EXPIRATION_MINUTES', 15)

    send_mail(
        'Tu codigo de verificacion',
        f'Tu codigo de verificacion es: {codigo}. Expira en {minutos} minutos.',
        settings.DEFAULT_FROM_EMAIL,
        [usuario.email],
        fail_silently=False,
    )

    return challenge
