from rest_framework import viewsets
from rest_framework.decorators import action
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
from myapps.usuarios.permissions import IsUsuarioConRolActivoOrAdministradorWrite


def usuario_ve_todo(user):
    return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))


class EstadoRiegoViewSet(viewsets.ModelViewSet):
    queryset = EstadoRiego.objects.all()
    serializer_class = EstadoRiegoSerializer
    permission_classes = [IsUsuarioConRolActivoOrAdministradorWrite]

    def get_queryset(self):
        if usuario_ve_todo(self.request.user):
            return self.queryset

        return self.queryset.filter(actuador__nodo__parcela__finca__usuario=self.request.user)

    @action(detail=False, methods=['get'])
    def latest(self, request):
        ultimo = self.get_queryset().order_by('-fecha_hora_inicio').first()
        if ultimo:
            return Response(self.get_serializer(ultimo).data)
        return Response({'mensaje': 'No hay estados de riego'})


class ReglaRiegoAutomaticoViewSet(viewsets.ModelViewSet):
    queryset = ReglaRiegoAutomatico.objects.all()
    serializer_class = ReglaRiegoAutomaticoSerializer
    permission_classes = [IsUsuarioConRolActivoOrAdministradorWrite]

    def get_queryset(self):
        if usuario_ve_todo(self.request.user):
            return self.queryset

        return self.queryset.filter(parcela__finca__usuario=self.request.user)


class ComandoRiegoViewSet(viewsets.ModelViewSet):
    queryset = ComandoRiego.objects.all()
    serializer_class = ComandoRiegoSerializer
    permission_classes = [IsUsuarioConRolActivoOrAdministradorWrite]

    def get_queryset(self):
        if usuario_ve_todo(self.request.user):
            return self.queryset

        return self.queryset.filter(actuador__nodo__parcela__finca__usuario=self.request.user)

    def _crear_comando_manual(self, request, comando):
        serializer = ComandoManualSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        actuadores = Actuador.objects.all()
        if not usuario_ve_todo(request.user):
            actuadores = actuadores.filter(nodo__parcela__finca__usuario=request.user)

        actuador = get_object_or_404(actuadores, id=serializer.validated_data['actuador_id'])
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
    permission_classes = [IsUsuarioConRolActivoOrAdministradorWrite]

    def get_queryset(self):
        if usuario_ve_todo(self.request.user):
            return self.queryset

        return self.queryset.filter(comando__actuador__nodo__parcela__finca__usuario=self.request.user)
