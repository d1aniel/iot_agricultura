from django.contrib import admin

from myapps.usuarios.models import AuthToken, LoginChallenge, Rol, TwoFactorDevice, UsuarioPerfil, UsuarioRol


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


@admin.register(TwoFactorDevice)
class TwoFactorDeviceAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'confirmado', 'fecha_creacion', 'fecha_confirmacion')
    list_filter = ('confirmado',)
    search_fields = ('usuario__username',)
    readonly_fields = ('secret', 'fecha_creacion', 'fecha_confirmacion')


@admin.register(LoginChallenge)
class LoginChallengeAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'proposito', 'challenge_id', 'fecha_creacion', 'fecha_expiracion', 'usado')
    list_filter = ('proposito', 'usado', 'fecha_creacion', 'fecha_expiracion')
    search_fields = ('usuario__username', 'challenge_id')
    readonly_fields = ('challenge_id', 'codigo_hash', 'fecha_creacion', 'fecha_expiracion')
