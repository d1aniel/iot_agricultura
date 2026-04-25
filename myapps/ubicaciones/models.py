from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Organizacion(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVA', 'Activa'),
        ('INACTIVA', 'Inactiva'),
    ]

    nombre = models.CharField(max_length=150)
    nit_documento = models.CharField(max_length=50, blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(max_length=120, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVA')

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'organizacion'
        verbose_name = 'organizacion'
        verbose_name_plural = 'organizaciones'


class Finca(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVA', 'Activa'),
        ('INACTIVA', 'Inactiva'),
    ]

    organizacion = models.ForeignKey(
        Organizacion,
        on_delete=models.CASCADE,
        related_name='fincas',
        null=True,
        blank=True,
    )
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=150)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    latitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    area_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unidad_area = models.CharField(max_length=20, default='hectareas')
    fecha_creacion = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVA')

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'finca'
        verbose_name = 'finca'
        verbose_name_plural = 'fincas'


class Parcela(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVA', 'Activa'),
        ('INACTIVA', 'Inactiva'),
    ]

    finca = models.ForeignKey(Finca, on_delete=models.CASCADE, related_name='parcelas')
    nombre = models.CharField(max_length=150)
    tipo_cultivo = models.CharField(max_length=100)
    area = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_area = models.CharField(max_length=20, default='m2')
    tipo_suelo = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVA')

    def __str__(self):
        return f'{self.nombre} - {self.finca}'

    class Meta:
        db_table = 'parcela'
        verbose_name = 'parcela'
        verbose_name_plural = 'parcelas'
