from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.utils import timezone
import hashlib
import secrets


class UsuarioPerfil(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('BLOQUEADO', 'Bloqueado'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_iot')
    organizacion = models.ForeignKey(
        'ubicaciones.Organizacion',
        on_delete=models.CASCADE,
        related_name='usuarios',
        null=True,
        blank=True,
    )
    telefono = models.CharField(max_length=30, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVO')
    ultimo_acceso = models.DateTimeField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.usuario.get_full_name() or self.usuario.username

    class Meta:
        db_table = 'usuario'
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'


class Rol(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
    ]

    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVO')

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'rol'
        verbose_name = 'rol'
        verbose_name_plural = 'roles'


class UsuarioRol(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
    ]

    usuario = models.ForeignKey(UsuarioPerfil, on_delete=models.CASCADE, related_name='roles')
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name='usuarios')
    fecha_asignacion = models.DateTimeField(default=timezone.now)
    asignado_por = models.ForeignKey(
        UsuarioPerfil,
        on_delete=models.SET_NULL,
        related_name='roles_asignados',
        null=True,
        blank=True,
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVO')

    def __str__(self):
        return f'{self.usuario} - {self.rol}'

    class Meta:
        db_table = 'usuario_rol'
        verbose_name = 'usuario rol'
        verbose_name_plural = 'usuarios roles'
        unique_together = ('usuario', 'rol')


class AuthToken(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens_api')
    token_hash = models.CharField(max_length=64, unique=True)
    nombre_dispositivo = models.CharField(max_length=120, blank=True, null=True)
    direccion_ip = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    ultimo_uso = models.DateTimeField(blank=True, null=True)
    fecha_expiracion = models.DateTimeField()
    revocado = models.BooleanField(default=False)

    @staticmethod
    def hash_token(token):
        return hashlib.sha256(token.encode('utf-8')).hexdigest()

    @classmethod
    def crear_token(cls, usuario, nombre_dispositivo=None, direccion_ip=None, user_agent=None):
        token = secrets.token_urlsafe(48)
        dias_expiracion = getattr(settings, 'AUTH_TOKEN_EXPIRATION_DAYS', 7)
        cls.objects.create(
            usuario=usuario,
            token_hash=cls.hash_token(token),
            nombre_dispositivo=nombre_dispositivo,
            direccion_ip=direccion_ip,
            user_agent=user_agent,
            fecha_expiracion=timezone.now() + timezone.timedelta(days=dias_expiracion),
        )
        return token

    @property
    def esta_activo(self):
        return not self.revocado and self.fecha_expiracion > timezone.now()

    def __str__(self):
        return f'Token API de {self.usuario.username}'

    class Meta:
        db_table = 'auth_token_api'
        verbose_name = 'token de autenticacion'
        verbose_name_plural = 'tokens de autenticacion'


class TwoFactorDevice(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dispositivo_2fa')
    secret = models.CharField(max_length=64, blank=True, null=True)
    confirmado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_confirmacion = models.DateTimeField(blank=True, null=True)
    ultimo_codigo_usado = models.CharField(max_length=12, blank=True, null=True)

    def __str__(self):
        estado = 'activo' if self.confirmado else 'pendiente'
        return f'2FA {estado} de {self.usuario.username}'

    class Meta:
        db_table = 'two_factor_device'
        verbose_name = 'dispositivo 2FA'
        verbose_name_plural = 'dispositivos 2FA'


class LoginChallenge(models.Model):
    PROPOSITO_CHOICES = [
        ('LOGIN', 'Inicio de sesion'),
        ('ACTIVAR_2FA', 'Activar 2FA'),
        ('DESACTIVAR_2FA', 'Desactivar 2FA'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='retos_login')
    challenge_id = models.CharField(max_length=64, unique=True, default=secrets.token_urlsafe)
    codigo_hash = models.CharField(max_length=64, blank=True, null=True)
    proposito = models.CharField(max_length=30, choices=PROPOSITO_CHOICES, default='LOGIN')
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_expiracion = models.DateTimeField()
    direccion_ip = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    usado = models.BooleanField(default=False)

    @classmethod
    def hash_codigo(codigo):
        return hashlib.sha256(codigo.encode('utf-8')).hexdigest()

    @classmethod
    def crear(cls, usuario, codigo=None, direccion_ip=None, user_agent=None, proposito='LOGIN'):
        minutos_expiracion = getattr(settings, 'EMAIL_OTP_EXPIRATION_MINUTES', 15)
        return cls.objects.create(
            usuario=usuario,
            codigo_hash=cls.hash_codigo(codigo) if codigo else None,
            proposito=proposito,
            direccion_ip=direccion_ip,
            user_agent=user_agent,
            fecha_expiracion=timezone.now() + timezone.timedelta(minutes=minutos_expiracion),
        )

    @property
    def esta_activo(self):
        return not self.usado and self.fecha_expiracion > timezone.now()

    def verificar_codigo(self, codigo):
        if not self.codigo_hash or not codigo:
            return False
        return secrets.compare_digest(self.codigo_hash, self.hash_codigo(codigo))

    def __str__(self):
        return f'Reto 2FA de {self.usuario.username}'

    class Meta:
        db_table = 'login_challenge'
        verbose_name = 'reto de login'
        verbose_name_plural = 'retos de login'
