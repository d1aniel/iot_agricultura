from rest_framework import viewsets

from myapps.usuarios.models import Rol, UsuarioPerfil, UsuarioRol
from myapps.usuarios.serializers import RolSerializer, UsuarioPerfilSerializer, UsuarioRolSerializer


class UsuarioPerfilViewSet(viewsets.ModelViewSet):
    queryset = UsuarioPerfil.objects.all()
    serializer_class = UsuarioPerfilSerializer


class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer


class UsuarioRolViewSet(viewsets.ModelViewSet):
    queryset = UsuarioRol.objects.all()
    serializer_class = UsuarioRolSerializer
