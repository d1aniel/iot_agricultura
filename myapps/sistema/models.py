from django.db import models


class AlertaSistema(models.Model):
    SEVERIDAD_CHOICES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
        ('CRITICA', 'Critica'),
    ]
    ESTADO_CHOICES = [
        ('ABIERTA', 'Abierta'),
        ('ATENDIDA', 'Atendida'),
        ('CERRADA', 'Cerrada'),
    ]

    nodo = models.ForeignKey(
        'iot.NodoIoT',
        on_delete=models.SET_NULL,
        related_name='alertas',
        null=True,
        blank=True,
    )
    sensor = models.ForeignKey(
        'iot.Sensor',
        on_delete=models.SET_NULL,
        related_name='alertas',
        null=True,
        blank=True,
    )
    actuador = models.ForeignKey(
        'iot.Actuador',
        on_delete=models.SET_NULL,
        related_name='alertas',
        null=True,
        blank=True,
    )
    tipo_alerta = models.CharField(max_length=80)
    severidad = models.CharField(max_length=20, choices=SEVERIDAD_CHOICES)
    mensaje = models.TextField()
    fecha_hora = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='ABIERTA')
    atendida_por = models.ForeignKey(
        'usuarios.UsuarioPerfil',
        on_delete=models.SET_NULL,
        related_name='alertas_atendidas',
        null=True,
        blank=True,
    )
    fecha_atencion = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.tipo_alerta} - {self.severidad}'

    class Meta:
        db_table = 'alerta_sistema'
        verbose_name = 'alerta del sistema'
        verbose_name_plural = 'alertas del sistema'
        ordering = ('-fecha_hora',)


class AuditoriaSistema(models.Model):
    ACCION_CHOICES = [
        ('CREAR', 'Crear'),
        ('ACTUALIZAR', 'Actualizar'),
        ('ELIMINAR', 'Eliminar'),
        ('INICIAR_SESION', 'Iniciar sesion'),
        ('ENVIAR_COMANDO', 'Enviar comando'),
    ]

    usuario = models.ForeignKey(
        'usuarios.UsuarioPerfil',
        on_delete=models.SET_NULL,
        related_name='auditorias',
        null=True,
        blank=True,
    )
    tabla_afectada = models.CharField(max_length=80)
    id_registro_afectado = models.PositiveIntegerField(blank=True, null=True)
    accion = models.CharField(max_length=30, choices=ACCION_CHOICES)
    descripcion = models.TextField()
    valor_anterior = models.JSONField(blank=True, null=True)
    valor_nuevo = models.JSONField(blank=True, null=True)
    direccion_ip = models.GenericIPAddressField(blank=True, null=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.accion} - {self.tabla_afectada}'

    class Meta:
        db_table = 'auditoria_sistema'
        verbose_name = 'auditoria del sistema'
        verbose_name_plural = 'auditorias del sistema'
        ordering = ('-fecha_hora',)
