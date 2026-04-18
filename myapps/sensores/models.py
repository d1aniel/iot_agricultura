from django.db import models
from myapps.devices.models import Device

class Sensor(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    temperatura = models.FloatField(help_text="Temperatura registrada")
    humedad = models.FloatField(help_text="Humedad registrada")
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device} - {self.temperatura}°C"

    class Meta:
        verbose_name = "sensor"
        verbose_name_plural = "sensores"