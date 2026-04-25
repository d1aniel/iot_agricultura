from django.contrib import admin

from myapps.riego.models import ComandoRiego, EstadoRiego, ReglaRiegoAutomatico, RespuestaComando


@admin.register(EstadoRiego)
class EstadoRiegoAdmin(admin.ModelAdmin):
    list_display = ('id', 'actuador', 'estado', 'modo', 'fecha_hora_inicio', 'fecha_hora_fin')
    list_filter = ('estado', 'modo', 'fecha_hora_inicio')
    search_fields = ('actuador__nombre', 'actuador__nodo__codigo_nodo')
    readonly_fields = ('fecha_hora_inicio',)


@admin.register(ReglaRiegoAutomatico)
class ReglaRiegoAutomaticoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',
        'parcela',
        'actuador',
        'sensor_humedad',
        'humedad_encendido',
        'humedad_apagado',
        'activa',
    )
    list_filter = ('activa', 'parcela')
    search_fields = ('nombre', 'parcela__nombre', 'actuador__nombre', 'sensor_humedad__nombre')


@admin.register(ComandoRiego)
class ComandoRiegoAdmin(admin.ModelAdmin):
    list_display = ('id', 'actuador', 'comando', 'origen', 'estado_comando', 'fecha_hora_envio')
    list_filter = ('comando', 'origen', 'estado_comando', 'fecha_hora_envio')
    search_fields = ('actuador__nombre', 'actuador__nodo__codigo_nodo')
    readonly_fields = ('fecha_hora_envio',)


@admin.register(RespuestaComando)
class RespuestaComandoAdmin(admin.ModelAdmin):
    list_display = ('id', 'comando', 'respuesta', 'codigo_error', 'fecha_hora_respuesta')
    list_filter = ('respuesta', 'fecha_hora_respuesta')
    search_fields = ('respuesta', 'mensaje', 'codigo_error')
    readonly_fields = ('fecha_hora_respuesta',)
