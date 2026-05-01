from django.core.mail import BadHeaderError
from django.db import transaction
from django.utils import timezone
from smtplib import SMTPException

from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from myapps.sistema.models import AuditoriaSistema
from myapps.usuarios.models import AuthToken, Rol, TwoFactorDevice, UsuarioPerfil, UsuarioRol
from myapps.usuarios.serializers import (
    AuthTokenSerializer,
    LoginSerializer,
    RegistroSerializer,
    RolSerializer,
    TwoFactorConfirmSerializer,
    UserSerializer,
    UsuarioPerfilSerializer,
    UsuarioRolSerializer,
    Verificar2FASerializer,
)
from myapps.usuarios.email_otp import enviar_codigo_otp_email


class UsuarioPerfilViewSet(viewsets.ModelViewSet):
    queryset = UsuarioPerfil.objects.all()
    serializer_class = UsuarioPerfilSerializer
    permission_classes = [IsAuthenticated]


class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [IsAdminUser]


class UsuarioRolViewSet(viewsets.ModelViewSet):
    queryset = UsuarioRol.objects.all()
    serializer_class = UsuarioRolSerializer
    permission_classes = [IsAdminUser]


def obtener_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def registrar_auditoria_login(user, request, descripcion):
    perfil = UsuarioPerfil.objects.filter(usuario=user).first()
    AuditoriaSistema.objects.create(
        usuario=perfil,
        tabla_afectada='auth',
        accion='INICIAR_SESION',
        descripcion=descripcion,
        direccion_ip=obtener_ip(request),
    )


def crear_respuesta_token(user, request, nombre_dispositivo=None):
    token = AuthToken.crear_token(
        usuario=user,
        nombre_dispositivo=nombre_dispositivo,
        direccion_ip=obtener_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
    )
    perfil = UsuarioPerfil.objects.filter(usuario=user).first()
    if perfil:
        perfil.ultimo_acceso = timezone.now()
        perfil.save(update_fields=['ultimo_acceso'])
    registrar_auditoria_login(user, request, 'Inicio de sesion exitoso')
    return Response({
        'token': token,
        'tipo': 'Token',
        'usuario': UserSerializer(user).data,
    })


class RegistroView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                user = serializer.save()
                TwoFactorDevice.objects.create(usuario=user, secret='', confirmado=False)
                challenge = enviar_codigo_otp_email(
                    usuario=user,
                    direccion_ip=obtener_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    proposito='ACTIVAR_2FA',
                )
        except (SMTPException, OSError, BadHeaderError):
            return Response(
                {'detail': 'No se pudo enviar el codigo de verificacion. Revisa la configuracion SMTP del backend.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response({
            'usuario': UserSerializer(user).data,
            'requiere_2fa': True,
            'challenge_id': challenge.challenge_id,
            'expira_en': challenge.fecha_expiracion,
            'mensaje': 'Registro creado. Codigo de verificacion enviado al correo.',
        }, status=status.HTTP_201_CREATED)


class ConfirmarRegistro2FAView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TwoFactorConfirmSerializer(
            data=request.data,
            context={'proposito': 'ACTIVAR_2FA'},
        )
        serializer.is_valid(raise_exception=True)
        challenge = serializer.context['challenge']
        user = challenge.usuario
        device, _ = TwoFactorDevice.objects.get_or_create(usuario=user, defaults={'secret': ''})

        if not challenge.verificar_codigo(serializer.validated_data['codigo']):
            return Response({'detail': 'Codigo 2FA invalido.'}, status=status.HTTP_400_BAD_REQUEST)

        device.confirmado = True
        device.fecha_confirmacion = timezone.now()
        device.save(update_fields=['confirmado', 'fecha_confirmacion'])
        challenge.usado = True
        challenge.save(update_fields=['usado'])
        return crear_respuesta_token(user, request)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        dispositivo = getattr(user, 'dispositivo_2fa', None)

        if not user.email:
            return Response({'detail': 'El usuario no tiene correo configurado para 2FA.'}, status=status.HTTP_400_BAD_REQUEST)

        if not dispositivo:
            dispositivo = TwoFactorDevice.objects.create(usuario=user, secret='', confirmado=False)

        proposito = 'LOGIN' if dispositivo.confirmado else 'ACTIVAR_2FA'
        challenge = enviar_codigo_otp_email(
            usuario=user,
            direccion_ip=obtener_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            proposito=proposito,
        )
        return Response({
            'requiere_2fa': True,
            'challenge_id': challenge.challenge_id,
            'expira_en': challenge.fecha_expiracion,
            'mensaje': 'Codigo de verificacion enviado al correo.',
            '2fa_pendiente': not dispositivo.confirmado,
        }, status=status.HTTP_202_ACCEPTED)


class Verificar2FAView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = Verificar2FASerializer(data=request.data, context={'proposito': 'LOGIN'})
        serializer.is_valid(raise_exception=True)
        challenge = serializer.context['challenge']
        user = challenge.usuario
        dispositivo = getattr(user, 'dispositivo_2fa', None)

        if not dispositivo or not dispositivo.confirmado:
            return Response({'detail': 'El usuario no tiene 2FA activo.'}, status=status.HTTP_400_BAD_REQUEST)

        codigo = serializer.validated_data['codigo']
        if not challenge.verificar_codigo(codigo):
            return Response({'detail': 'Codigo 2FA invalido.'}, status=status.HTTP_400_BAD_REQUEST)

        challenge.usado = True
        challenge.save(update_fields=['usado'])
        return crear_respuesta_token(user, request, serializer.validated_data.get('nombre_dispositivo'))


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if isinstance(request.auth, AuthToken):
            request.auth.revocado = True
            request.auth.save(update_fields=['revocado'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class PerfilActualView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class TwoFactorSetupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.email:
            return Response({'detail': 'Tu usuario no tiene correo configurado.'}, status=status.HTTP_400_BAD_REQUEST)

        device, created = TwoFactorDevice.objects.get_or_create(
            usuario=request.user,
            defaults={'secret': ''},
        )
        if not created and device.confirmado:
            return Response({'detail': '2FA ya esta activo.'}, status=status.HTTP_400_BAD_REQUEST)

        challenge = enviar_codigo_otp_email(
            usuario=request.user,
            direccion_ip=obtener_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            proposito='ACTIVAR_2FA',
        )
        return Response({
            'challenge_id': challenge.challenge_id,
            'expira_en': challenge.fecha_expiracion,
            'confirmado': device.confirmado,
            'mensaje': 'Codigo de activacion enviado al correo.',
        })


class TwoFactorConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TwoFactorConfirmSerializer(
            data=request.data,
            context={'request': request, 'proposito': 'ACTIVAR_2FA'},
        )
        serializer.is_valid(raise_exception=True)
        device = getattr(request.user, 'dispositivo_2fa', None)

        if not device:
            return Response({'detail': 'Primero solicita el codigo 2FA.'}, status=status.HTTP_400_BAD_REQUEST)

        codigo = serializer.validated_data['codigo']
        challenge = serializer.context['challenge']
        if not challenge.verificar_codigo(codigo):
            return Response({'detail': 'Codigo 2FA invalido.'}, status=status.HTTP_400_BAD_REQUEST)

        device.confirmado = True
        device.fecha_confirmacion = timezone.now()
        device.save(update_fields=['confirmado', 'fecha_confirmacion'])
        challenge.usado = True
        challenge.save(update_fields=['usado'])
        return Response({'detail': '2FA activado correctamente.'})


class TwoFactorDisableView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({'detail': 'La verificacion en dos pasos es obligatoria y no se puede desactivar.'}, status=status.HTTP_400_BAD_REQUEST)


class AuthTokenViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuthTokenSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AuthToken.objects.filter(usuario=self.request.user).order_by('-fecha_creacion')
