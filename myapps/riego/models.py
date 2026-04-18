from django.db import models
from myapps.devices.models import Device

class Riego(models.Model):
    MODO_CHOICES = [
        ('AUTO', 'Automático'),
        ('MANUAL', 'Manual'),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    estado = models.BooleanField(help_text="Estado del riego (encendido/apagado)")
    modo = models.CharField(max_length=10, choices=MODO_CHOICES)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device} - {self.modo}"

    class Meta:
        verbose_name = "riego"
        verbose_name_plural = "riegos"