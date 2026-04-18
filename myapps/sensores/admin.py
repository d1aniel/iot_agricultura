from django.contrib import admin
from myapps.sensores.models import Sensor

class SensorAdmin(admin.ModelAdmin):
    list_display = ('id', 'temperatura', 'humedad', 'fecha')
    list_filter = ('fecha',)
    search_fields = ('id',)
    ordering = ('-fecha',)

    readonly_fields = ('fecha',)

    fieldsets = (
        ('Datos del Sensor', {
            'fields': ('temperatura', 'humedad', 'device')  # ✅ AGREGA device
        }),
        ('Registro', {
            'fields': ('fecha',)
        }),
    )

admin.site.register(Sensor, SensorAdmin)