from django.contrib import admin

from myapps.usuarios.models import AuthToken, Rol, UsuarioPerfil, UsuarioRol


@admin.register(UsuarioPerfil)
class UsuarioPerfilAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'organizacion', 'telefono', 'estado')
    list_filter = ('organizacion', 'estado')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'usuario__email')


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'estado')
    list_filter = ('estado',)
    search_fields = ('nombre',)


@admin.register(UsuarioRol)
class UsuarioRolAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'rol', 'asignado_por', 'estado')
    list_filter = ('rol', 'estado')
    search_fields = ('usuario__usuario__username', 'rol__nombre')


@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'nombre_dispositivo', 'fecha_creacion', 'fecha_expiracion', 'revocado')
    list_filter = ('revocado', 'fecha_creacion', 'fecha_expiracion')
    search_fields = ('usuario__username', 'nombre_dispositivo')
    readonly_fields = ('token_hash', 'fecha_creacion', 'ultimo_uso')
