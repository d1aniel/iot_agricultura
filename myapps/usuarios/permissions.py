from rest_framework.permissions import BasePermission


ROLES_ADMINISTRATIVOS = {'administrador', 'admin', 'auditor'}


def usuario_tiene_rol_administrativo(user):
    if not user or not user.is_authenticated:
        return False

    if user.is_staff or user.is_superuser:
        return True

    perfil = getattr(user, 'perfil_iot', None)
    if not perfil:
        return False

    return perfil.roles.filter(
        estado='ACTIVO',
        rol__estado='ACTIVO',
        rol__nombre__iexact='Administrador',
    ).exists() or perfil.roles.filter(
        estado='ACTIVO',
        rol__estado='ACTIVO',
        rol__nombre__iexact='Admin',
    ).exists() or perfil.roles.filter(
        estado='ACTIVO',
        rol__estado='ACTIVO',
        rol__nombre__iexact='Auditor',
    ).exists()


def usuario_tiene_rol_activo(user):
    if not user or not user.is_authenticated:
        return False

    if user.is_staff or user.is_superuser:
        return True

    perfil = getattr(user, 'perfil_iot', None)
    if not perfil:
        return False

    return perfil.roles.filter(estado='ACTIVO', rol__estado='ACTIVO').exists()


class IsUsuarioConRolActivo(BasePermission):
    message = 'Tu usuario aun no tiene un rol activo asignado.'

    def has_permission(self, request, view):
        return usuario_tiene_rol_activo(request.user)


class IsAdministradorOrAuditor(BasePermission):
    message = 'Solo usuarios con rol Administrador o Auditor pueden acceder a este modulo.'

    def has_permission(self, request, view):
        return usuario_tiene_rol_administrativo(request.user)
