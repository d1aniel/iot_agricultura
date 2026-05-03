from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from myapps.iot.models import NodoIoT
from myapps.iot.serializers import NodoIoTSerializer
from myapps.ubicaciones.models import Finca, Organizacion, Parcela
from myapps.ubicaciones.serializers import FincaSerializer, OrganizacionSerializer, ParcelaSerializer
from myapps.usuarios.permissions import IsUsuarioConRolActivo


class OrganizacionViewSet(viewsets.ModelViewSet):
    queryset = Organizacion.objects.all()
    serializer_class = OrganizacionSerializer
    permission_classes = [IsUsuarioConRolActivo]


class FincaViewSet(viewsets.ModelViewSet):
    queryset = Finca.objects.all()
    serializer_class = FincaSerializer
    permission_classes = [IsUsuarioConRolActivo]


class ParcelaViewSet(viewsets.ModelViewSet):
    queryset = Parcela.objects.all()
    serializer_class = ParcelaSerializer
    permission_classes = [IsUsuarioConRolActivo]


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
