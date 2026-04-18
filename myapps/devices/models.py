from django.db import models

class Device(models.Model):
    nombre = models.CharField(max_length=50, help_text="Nombre del dispositivo")
    ubicacion = models.CharField(max_length=100, help_text="Ubicación del dispositivo")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "device"
        verbose_name_plural = "devices"