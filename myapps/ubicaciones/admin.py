from django.contrib import admin

from myapps.ubicaciones.models import Finca, Organizacion, Parcela


@admin.register(Organizacion)
class OrganizacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'email', 'telefono', 'estado')
    list_filter = ('estado',)
    search_fields = ('nombre', 'nit_documento', 'email')


@admin.register(Finca)
class FincaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'ubicacion', 'organizacion', 'usuario', 'estado')
    list_filter = ('organizacion', 'estado')
    search_fields = ('nombre', 'ubicacion')


@admin.register(Parcela)
class ParcelaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'finca', 'tipo_cultivo', 'area', 'estado')
    list_filter = ('finca', 'tipo_cultivo', 'estado')
    search_fields = ('nombre', 'tipo_cultivo')
