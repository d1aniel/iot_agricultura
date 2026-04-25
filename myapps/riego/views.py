from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from myapps.iot.models import Actuador
from myapps.riego.models import ComandoRiego, EstadoRiego, ReglaRiegoAutomatico, RespuestaComando
from myapps.riego.serializers import (
    ComandoManualSerializer,
    ComandoRiegoSerializer,
    EstadoRiegoSerializer,
    ReglaRiegoAutomaticoSerializer,
    RespuestaComandoSerializer,
)
from myapps.usuarios.models import UsuarioPerfil


class EstadoRiegoViewSet(viewsets.ModelViewSet):
    queryset = EstadoRiego.objects.all()
    serializer_class = EstadoRiegoSerializer

    @action(detail=False, methods=['get'])
    def latest(self, request):
        ultimo = EstadoRiego.objects.order_by('-fecha_hora_inicio').first()
        if ultimo:
            return Response(self.get_serializer(ultimo).data)
        return Response({'mensaje': 'No hay estados de riego'})


class ReglaRiegoAutomaticoViewSet(viewsets.ModelViewSet):
    queryset = ReglaRiegoAutomatico.objects.all()
    serializer_class = ReglaRiegoAutomaticoSerializer


class ComandoRiegoViewSet(viewsets.ModelViewSet):
    queryset = ComandoRiego.objects.all()
    serializer_class = ComandoRiegoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def _crear_comando_manual(self, request, comando):
        serializer = ComandoManualSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        actuador = get_object_or_404(Actuador, id=serializer.validated_data['actuador_id'])
        usuario_perfil = None

        if request.user and request.user.is_authenticated:
            usuario_perfil = UsuarioPerfil.objects.filter(usuario=request.user).first()

        comando_riego = ComandoRiego.objects.create(
            actuador=actuador,
            usuario=usuario_perfil,
            comando=comando,
            origen='MANUAL',
            estado_comando='PENDIENTE',
            parametro={'medio': 'pagina_web'},
        )

        return Response(ComandoRiegoSerializer(comando_riego).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='activar-manual')
    def activar_manual(self, request):
        return self._crear_comando_manual(request, 'ENCENDER')

    @action(detail=False, methods=['post'], url_path='desactivar-manual')
    def desactivar_manual(self, request):
        return self._crear_comando_manual(request, 'APAGAR')


class RespuestaComandoViewSet(viewsets.ModelViewSet):
    queryset = RespuestaComando.objects.all()
    serializer_class = RespuestaComandoSerializer
