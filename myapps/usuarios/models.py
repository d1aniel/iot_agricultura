from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


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
