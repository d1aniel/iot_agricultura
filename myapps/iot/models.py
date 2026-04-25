from django.db import models


class NodoIoT(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('MANTENIMIENTO', 'Mantenimiento'),
        ('DESCONECTADO', 'Desconectado'),
    ]

    parcela = models.ForeignKey(
        'ubicaciones.Parcela',
        on_delete=models.CASCADE,
        related_name='nodos_iot',
        null=True,
        blank=True,
    )
    codigo_nodo = models.CharField(max_length=80, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    ubicacion = models.CharField(max_length=150, blank=True, null=True)
    direccion_ip = models.GenericIPAddressField(blank=True, null=True)
    mac_address = models.CharField(max_length=30, blank=True, null=True)
    fecha_instalacion = models.DateField(blank=True, null=True)
    ultima_conexion = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='ACTIVO')

    def __str__(self):
        return f'{self.nombre} ({self.codigo_nodo})'

    class Meta:
        db_table = 'nodo_iot'
        verbose_name = 'nodo IoT'
        verbose_name_plural = 'nodos IoT'


class Sensor(models.Model):
    TIPO_CHOICES = [
        ('TEMPERATURA', 'Temperatura'),
        ('HUMEDAD_AMBIENTE', 'Humedad ambiente'),
        ('HUMEDAD_SUELO', 'Humedad del suelo'),
        ('LLUVIA', 'Lluvia'),
        ('LUZ', 'Luz'),
    ]
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('DANADO', 'Danado'),
    ]

    nodo = models.ForeignKey(NodoIoT, on_delete=models.CASCADE, related_name='sensores')
    nombre = models.CharField(max_length=100)
    tipo_sensor = models.CharField(max_length=50, choices=TIPO_CHOICES)
    modelo = models.CharField(max_length=50, default='DHT11')
    unidad_medida = models.CharField(max_length=20)
    pin_conexion = models.CharField(max_length=20, blank=True, null=True)
    valor_minimo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_maximo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVO')
    fecha_instalacion = models.DateField(blank=True, null=True)

    def __str__(self):
        return f'{self.nombre} - {self.nodo}'

    class Meta:
        db_table = 'sensor'
        verbose_name = 'sensor'
        verbose_name_plural = 'sensores'


class LecturaSensor(models.Model):
    CALIDAD_CHOICES = [
        ('VALIDO', 'Valido'),
        ('SOSPECHOSO', 'Sospechoso'),
        ('ERROR', 'Error'),
    ]

    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='lecturas')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.CharField(max_length=20)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    calidad_dato = models.CharField(max_length=30, choices=CALIDAD_CHOICES, default='VALIDO')
    observacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.sensor} - {self.valor} {self.unidad_medida}'

    class Meta:
        db_table = 'lectura_sensor'
        verbose_name = 'lectura de sensor'
        verbose_name_plural = 'lecturas de sensores'
        ordering = ('-fecha_hora',)


class Actuador(models.Model):
    TIPO_CHOICES = [
        ('RELE', 'Rele'),
        ('BOMBA', 'Bomba'),
        ('VALVULA', 'Valvula'),
        ('MOTOR', 'Motor'),
    ]
    ESTADO_ACTUAL_CHOICES = [
        ('ENCENDIDO', 'Encendido'),
        ('APAGADO', 'Apagado'),
        ('ERROR', 'Error'),
    ]
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('MANTENIMIENTO', 'Mantenimiento'),
    ]

    nodo = models.ForeignKey(NodoIoT, on_delete=models.CASCADE, related_name='actuadores')
    nombre = models.CharField(max_length=100)
    tipo_actuador = models.CharField(max_length=50, choices=TIPO_CHOICES, default='RELE')
    modelo = models.CharField(max_length=80, blank=True, null=True)
    pin_conexion = models.CharField(max_length=20, blank=True, null=True)
    estado_actual = models.CharField(max_length=20, choices=ESTADO_ACTUAL_CHOICES, default='APAGADO')
    fecha_instalacion = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVO')

    def __str__(self):
        return f'{self.nombre} - {self.nodo}'

    class Meta:
        db_table = 'actuador'
        verbose_name = 'actuador'
        verbose_name_plural = 'actuadores'
