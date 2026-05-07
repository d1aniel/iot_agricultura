from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from myapps.iot.models import NodoIoT
from myapps.iot.serializers import NodoIoTSerializer
from myapps.ubicaciones.models import Finca, Organizacion, Parcela
from myapps.ubicaciones.serializers import FincaSerializer, OrganizacionSerializer, ParcelaSerializer
from myapps.usuarios.permissions import IsUsuarioConRolActivo, usuario_tiene_rol_administrativo


def perfil_actual(user):
    return getattr(user, 'perfil_iot', None)


class OrganizacionViewSet(viewsets.ModelViewSet):
    queryset = Organizacion.objects.all()
    serializer_class = OrganizacionSerializer
    permission_classes = [IsUsuarioConRolActivo]

    def get_queryset(self):
        if usuario_tiene_rol_administrativo(self.request.user):
            return self.queryset

        perfil = perfil_actual(self.request.user)
        if not perfil or not perfil.organizacion_id:
            return self.queryset.none()

        return self.queryset.filter(id=perfil.organizacion_id)


class FincaViewSet(viewsets.ModelViewSet):
    queryset = Finca.objects.all()
    serializer_class = FincaSerializer
    permission_classes = [IsUsuarioConRolActivo]

    def get_queryset(self):
        if usuario_tiene_rol_administrativo(self.request.user):
            return self.queryset

        perfil = perfil_actual(self.request.user)
        queryset = self.queryset.filter(usuario=self.request.user)
        if perfil and perfil.organizacion_id:
            queryset = queryset | self.queryset.filter(organizacion_id=perfil.organizacion_id, usuario=self.request.user)

        return queryset.distinct()


class ParcelaViewSet(viewsets.ModelViewSet):
    queryset = Parcela.objects.all()
    serializer_class = ParcelaSerializer
    permission_classes = [IsUsuarioConRolActivo]

    def get_queryset(self):
        if usuario_tiene_rol_administrativo(self.request.user):
            return self.queryset

        return self.queryset.filter(finca__usuario=self.request.user)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated, IsUsuarioConRolActivo]

    def get(self, request):
        usuario = request.user
        finca = Finca.objects.filter(usuario=usuario).first()

        if not finca:
            return Response({'error': 'No tienes finca registrada'})

        nodos = NodoIoT.objects.filter(parcela__finca=finca)

        return Response({
            'usuario': usuario.username,
            'finca': finca.nombre,
            'nodos_iot': NodoIoTSerializer(nodos, many=True).data,
        })
