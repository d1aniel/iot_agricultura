from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from myapps.iot.models import NodoIoT
from myapps.iot.serializers import NodoIoTSerializer
from myapps.ubicaciones.models import Finca, Organizacion, Parcela
from myapps.ubicaciones.serializers import FincaSerializer, OrganizacionSerializer, ParcelaSerializer
from myapps.usuarios.permissions import IsUsuarioConRolActivo, IsUsuarioConRolActivoOrAdministradorWrite


def perfil_actual(user):
    return getattr(user, 'perfil_iot', None)


def usuario_ve_todo(user):
    return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))


class OrganizacionViewSet(viewsets.ModelViewSet):
    queryset = Organizacion.objects.all()
    serializer_class = OrganizacionSerializer
    permission_classes = [IsUsuarioConRolActivoOrAdministradorWrite]

    def get_queryset(self):
        if usuario_ve_todo(self.request.user):
            return self.queryset

        perfil = perfil_actual(self.request.user)
        organizaciones_ids = set()

        if perfil and perfil.organizacion_id:
            organizaciones_ids.add(perfil.organizacion_id)

        organizaciones_ids.update(
            Finca.objects.filter(usuario=self.request.user, organizacion__isnull=False)
            .values_list('organizacion_id', flat=True)
        )

        if not organizaciones_ids:
            return self.queryset.none()

        return self.queryset.filter(id__in=organizaciones_ids)


class FincaViewSet(viewsets.ModelViewSet):
    queryset = Finca.objects.all()
    serializer_class = FincaSerializer
    permission_classes = [IsUsuarioConRolActivoOrAdministradorWrite]

    def get_queryset(self):
        if usuario_ve_todo(self.request.user):
            return self.queryset

        return self.queryset.filter(usuario=self.request.user)


class ParcelaViewSet(viewsets.ModelViewSet):
    queryset = Parcela.objects.all()
    serializer_class = ParcelaSerializer
    permission_classes = [IsUsuarioConRolActivoOrAdministradorWrite]

    def get_queryset(self):
        if usuario_ve_todo(self.request.user):
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
