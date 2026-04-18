from django.contrib import admin
from myapps.riego.models import Riego

class RiegoAdmin(admin.ModelAdmin):
    list_display = ('id', 'device', 'estado', 'modo', 'fecha')
    list_filter = ('estado', 'modo', 'fecha')
    search_fields = ('device__id',)
    list_editable = ('estado', 'modo')
    ordering = ('-fecha',)

    readonly_fields = ('fecha',)  

    fieldsets = (
        ('Relación', {
            'fields': ('device',)  
        }),
        ('Configuración de Riego', {
            'fields': ('estado', 'modo')
        }),
        ('Registro', {
            'fields': ('fecha',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('device')  

admin.site.register(Riego, RiegoAdmin)