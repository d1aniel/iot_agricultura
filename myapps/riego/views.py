from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import timedelta
from decimal import Decimal

from myapps.iot.mqtt_service import publish_control
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
from myapps.usuarios.permissions import IsUsuarioConRolActivoOrAdministradorWrite, usuario_tiene_rol_administrativo


def usuario_ve_todo(user):
    return bool(user and user.is_authenticated and (
        user.is_staff or user.is_superuser or usuario_tiene_rol_administrativo(user)
    ))


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

    @action(detail=False, methods=['get'], url_path='analitica')
    def analitica(self, request):
        actuador_id = request.query_params.get('actuador_id')
        dias = int(request.query_params.get('dias', 7))
        desde = timezone.now() - timedelta(days=dias)
        queryset = self.get_queryset().filter(fecha_hora_inicio__gte=desde)

        if actuador_id:
            queryset = queryset.filter(actuador_id=actuador_id)

        actuador = None
        if actuador_id:
            actuador = Actuador.objects.filter(id=actuador_id).first()
        if not actuador:
            actuador = queryset.order_by('-fecha_hora_inicio').first().actuador if queryset.exists() else None

        caudal = Decimal(str(getattr(actuador, 'caudal_galones_hora', 0) or 0))
        total_segundos = 0
        activaciones = 0
        serie_por_dia = {}
        ahora = timezone.now()

        for estado in queryset.filter(estado='ENCENDIDO').order_by('fecha_hora_inicio'):
            fin = estado.fecha_hora_fin or ahora
            duracion = estado.duracion_segundos
            if duracion is None:
                duracion = max(0, int((fin - estado.fecha_hora_inicio).total_seconds()))

            total_segundos += duracion
            activaciones += 1
            dia = estado.fecha_hora_inicio.date().isoformat()
            serie_por_dia[dia] = serie_por_dia.get(dia, 0) + duracion

        total_horas = Decimal(total_segundos) / Decimal(3600)
        total_galones = total_horas * caudal
        serie = []
        for dia, segundos in sorted(serie_por_dia.items()):
            horas = Decimal(segundos) / Decimal(3600)
            serie.append({
                'fecha': dia,
                'segundos': segundos,
                'horas': round(float(horas), 2),
                'galones': round(float(horas * caudal), 2),
            })

        return Response({
            'actuador_id': actuador.id if actuador else None,
            'actuador_nombre': actuador.nombre if actuador else '',
            'caudal_galones_hora': round(float(caudal), 2),
            'periodo_dias': dias,
            'tiempo_total_segundos': total_segundos,
            'tiempo_total_horas': round(float(total_horas), 2),
            'agua_total_galones': round(float(total_galones), 2),
            'activaciones': activaciones,
            'serie_diaria': serie,
        })


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

    def _crear_comando_manual(self, request, comando, mqtt_command):
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

        publicado = publish_control(mqtt_command)
        comando_riego.estado_comando = 'ENVIADO' if publicado else 'PENDIENTE'
        comando_riego.save(update_fields=['estado_comando'])

        return Response(ComandoRiegoSerializer(comando_riego).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='activar-manual')
    def activar_manual(self, request):
        return self._crear_comando_manual(request, 'ENCENDER', 'ON')

    @action(detail=False, methods=['post'], url_path='desactivar-manual')
    def desactivar_manual(self, request):
        return self._crear_comando_manual(request, 'APAGAR', 'OFF')

    @action(detail=False, methods=['post'], url_path='automatico-manual')
    def automatico_manual(self, request):
        return self._crear_comando_manual(request, 'AUTO', 'AUTO')


class RespuestaComandoViewSet(viewsets.ModelViewSet):
    queryset = RespuestaComando.objects.all()
    serializer_class = RespuestaComandoSerializer
    permission_classes = [IsUsuarioConRolActivoOrAdministradorWrite]

    def get_queryset(self):
        if usuario_ve_todo(self.request.user):
            return self.queryset

        return self.queryset.filter(comando__actuador__nodo__parcela__finca__usuario=self.request.user)
