import secrets

from django.conf import settings
from django.core.mail import send_mail

from myapps.usuarios.models import LoginChallenge


class EmailOTPDeliveryError(Exception):
    pass


def generar_codigo_otp():
    return f'{secrets.randbelow(1000000):06d}'


def _crear_mensaje_otp(codigo, minutos):
    return (
        'Tu codigo de verificacion',
        f'Tu codigo de verificacion es: {codigo}. Expira en {minutos} minutos.',
    )


def _enviar_con_sendgrid(destinatario, asunto, mensaje):
    api_key = getattr(settings, 'SENDGRID_API_KEY', '')
    from_email = getattr(settings, 'SENDGRID_FROM_EMAIL', '') or settings.DEFAULT_FROM_EMAIL

    if not from_email:
        raise EmailOTPDeliveryError('No hay remitente configurado para SendGrid.')

    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
    except ImportError as exc:
        raise EmailOTPDeliveryError('El paquete sendgrid no esta instalado.') from exc

    email = Mail(
        from_email=from_email,
        to_emails=destinatario,
        subject=asunto,
        plain_text_content=mensaje,
    )
    response = SendGridAPIClient(api_key).send(email)
    if response.status_code >= 400:
        raise EmailOTPDeliveryError(f'SendGrid respondio con estado {response.status_code}.')


def _enviar_con_smtp(destinatario, asunto, mensaje):
    send_mail(
        asunto,
        mensaje,
        settings.DEFAULT_FROM_EMAIL,
        [destinatario],
        fail_silently=False,
    )


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
    asunto, mensaje = _crear_mensaje_otp(codigo, minutos)

    try:
        if getattr(settings, 'SENDGRID_API_KEY', ''):
            _enviar_con_sendgrid(usuario.email, asunto, mensaje)
        else:
            _enviar_con_smtp(usuario.email, asunto, mensaje)
    except Exception as exc:
        challenge.delete()
        if isinstance(exc, EmailOTPDeliveryError):
            raise
        raise EmailOTPDeliveryError('No se pudo enviar el codigo de verificacion.') from exc

    return challenge
