from django.contrib import admin

from myapps.iot.models import Actuador, LecturaSensor, NodoIoT, Sensor


@admin.register(NodoIoT)
class NodoIoTAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo_nodo', 'nombre', 'parcela', 'ubicacion', 'estado', 'ultima_conexion')
    list_filter = ('estado', 'parcela')
    search_fields = ('codigo_nodo', 'nombre', 'mac_address', 'direccion_ip')


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'tipo_sensor', 'modelo', 'unidad_medida', 'nodo', 'estado')
    list_filter = ('tipo_sensor', 'modelo', 'estado')
    search_fields = ('nombre', 'modelo', 'nodo__codigo_nodo')


@admin.register(LecturaSensor)
class LecturaSensorAdmin(admin.ModelAdmin):
    list_display = ('id', 'sensor', 'valor', 'unidad_medida', 'calidad_dato', 'fecha_hora')
    list_filter = ('calidad_dato', 'fecha_hora')
    search_fields = ('sensor__nombre', 'sensor__nodo__codigo_nodo')
    readonly_fields = ('fecha_hora',)


@admin.register(Actuador)
class ActuadorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'tipo_actuador', 'nodo', 'estado_actual', 'estado')
    list_filter = ('tipo_actuador', 'estado_actual', 'estado')
    search_fields = ('nombre', 'modelo', 'nodo__codigo_nodo')
