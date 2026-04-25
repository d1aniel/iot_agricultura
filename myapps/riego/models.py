from django.db import models


class EstadoRiego(models.Model):
    ESTADO_CHOICES = [
        ('ENCENDIDO', 'Encendido'),
        ('APAGADO', 'Apagado'),
    ]
    MODO_CHOICES = [
        ('AUTOMATICO', 'Automatico'),
        ('MANUAL', 'Manual'),
        ('DISPOSITIVO', 'Decidido por ESP32'),
    ]

    actuador = models.ForeignKey(
        'iot.Actuador',
        on_delete=models.CASCADE,
        related_name='estados_riego',
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    modo = models.CharField(max_length=20, choices=MODO_CHOICES)
    fecha_hora_inicio = models.DateTimeField(auto_now_add=True)
    fecha_hora_fin = models.DateTimeField(blank=True, null=True)
    duracion_segundos = models.PositiveIntegerField(blank=True, null=True)
    motivo = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.actuador} - {self.estado} - {self.modo}'

    class Meta:
        db_table = 'estado_riego'
        verbose_name = 'estado de riego'
        verbose_name_plural = 'estados de riego'
        ordering = ('-fecha_hora_inicio',)


class ReglaRiegoAutomatico(models.Model):
    parcela = models.ForeignKey(
        'ubicaciones.Parcela',
        on_delete=models.CASCADE,
        related_name='reglas_riego',
    )
    actuador = models.ForeignKey(
        'iot.Actuador',
        on_delete=models.CASCADE,
        related_name='reglas_riego',
    )
    sensor_humedad = models.ForeignKey(
        'iot.Sensor',
        on_delete=models.CASCADE,
        related_name='reglas_riego',
    )
    nombre = models.CharField(max_length=100)
    humedad_encendido = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    humedad_apagado = models.DecimalField(max_digits=5, decimal_places=2, default=80.00)
    activa = models.BooleanField(default=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nombre} ({self.humedad_encendido}% - {self.humedad_apagado}%)'

    class Meta:
        db_table = 'regla_riego_automatico'
        verbose_name = 'regla de riego automatico'
        verbose_name_plural = 'reglas de riego automatico'


class ComandoRiego(models.Model):
    COMANDO_CHOICES = [
        ('ENCENDER', 'Encender'),
        ('APAGAR', 'Apagar'),
        ('REINICIAR', 'Reiniciar'),
    ]
    ORIGEN_CHOICES = [
        ('MANUAL', 'Manual'),
        ('AUTOMATICO', 'Automatico'),
        ('DISPOSITIVO', 'Decidido por ESP32'),
        ('SISTEMA', 'Sistema'),
    ]
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('ENVIADO', 'Enviado'),
        ('EJECUTADO', 'Ejecutado'),
        ('FALLIDO', 'Fallido'),
    ]

    actuador = models.ForeignKey(
        'iot.Actuador',
        on_delete=models.CASCADE,
        related_name='comandos_riego',
    )
    usuario = models.ForeignKey(
        'usuarios.UsuarioPerfil',
        on_delete=models.SET_NULL,
        related_name='comandos_riego',
        null=True,
        blank=True,
    )
    regla = models.ForeignKey(
        ReglaRiegoAutomatico,
        on_delete=models.SET_NULL,
        related_name='comandos_riego',
        null=True,
        blank=True,
    )
    comando = models.CharField(max_length=30, choices=COMANDO_CHOICES)
    origen = models.CharField(max_length=30, choices=ORIGEN_CHOICES)
    parametro = models.JSONField(blank=True, null=True)
    fecha_hora_envio = models.DateTimeField(auto_now_add=True)
    estado_comando = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='PENDIENTE')

    def __str__(self):
        return f'{self.comando} - {self.actuador}'

    class Meta:
        db_table = 'comando_riego'
        verbose_name = 'comando de riego'
        verbose_name_plural = 'comandos de riego'
        ordering = ('-fecha_hora_envio',)


class RespuestaComando(models.Model):
    comando = models.ForeignKey(
        ComandoRiego,
        on_delete=models.CASCADE,
        related_name='respuestas',
    )
    respuesta = models.CharField(max_length=100)
    mensaje = models.TextField(blank=True, null=True)
    codigo_error = models.CharField(max_length=50, blank=True, null=True)
    fecha_hora_respuesta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.respuesta} - {self.comando}'

    class Meta:
        db_table = 'respuesta_comando'
        verbose_name = 'respuesta de comando'
        verbose_name_plural = 'respuestas de comandos'
        ordering = ('-fecha_hora_respuesta',)
