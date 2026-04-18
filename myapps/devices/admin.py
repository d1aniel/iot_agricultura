from django.contrib import admin
from myapps.devices.models import Device

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'ubicacion')
    search_fields = ('nombre', 'ubicacion')
    ordering = ('nombre',)

    fieldsets = (
        ('Información del Dispositivo', {
            'fields': ('nombre', 'ubicacion')
        }),
    )

admin.site.register(Device, DeviceAdmin)