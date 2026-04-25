from django.contrib import admin

from myapps.sistema.models import AlertaSistema, AuditoriaSistema


@admin.register(AlertaSistema)
class AlertaSistemaAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_alerta', 'severidad', 'estado', 'fecha_hora', 'atendida_por')
    list_filter = ('severidad', 'estado', 'fecha_hora')
    search_fields = ('tipo_alerta', 'mensaje')
    readonly_fields = ('fecha_hora',)


@admin.register(AuditoriaSistema)
class AuditoriaSistemaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'tabla_afectada', 'accion', 'fecha_hora')
    list_filter = ('accion', 'tabla_afectada', 'fecha_hora')
    search_fields = ('tabla_afectada', 'descripcion', 'direccion_ip')
    readonly_fields = ('fecha_hora',)
