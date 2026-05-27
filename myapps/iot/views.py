from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from myapps.iot.models import Actuador, LecturaSensor, NodoIoT, Sensor
from myapps.iot.mqtt_service import guardar_lectura_mqtt, leer_lectura_mqtt, mqtt_status
from myapps.iot.serializers import (
    ActuadorSerializer,
    LecturaSensorSerializer,
    NodoIoTSerializer,
    SensorSerializer,
)
from myapps.usuarios.permissions import IsUsuarioConRolActivoOrAdministradorWrite, usuario_tiene_rol_administrativo


def usuario_ve_todo(user):
    return bool(user and user.is_authenticated and (
        user.is_staff or user.is_superuser or usuario_tiene_rol_administrativo(user)
    ))


class NodoIoTViewSet(viewsets.ModelViewSet):
    queryset = NodoIoT.objects.all()
    serializer_class = NodoIoTSerializer
    permission_classes = [IsUsuarioConRolActivoOrAdministradorWrite]

    def get_queryset(self):
        if usuario_ve_todo(self.request.user):
            return self.queryset

        return self.queryset.filter(parcela__finca__usuario=self.request.user)

    @action(detail=False, methods=['get'], url_path='mqtt-status')
    def mqtt_status(self, request):
        return Response(mqtt_status())

    @action(detail=False, methods=['post'], url_path='probar-lectura-mqtt')
    def probar_lectura_mqtt(self, request):
        lectura = guardar_lectura_mqtt(request.data)
        return Response(LecturaSensorSerializer(lectura).data)


class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [IsUsuarioConRolActivoOrAdministradorWrite]

    def get_queryset(self):
        if usuario_ve_todo(self.request.user):
            return self.queryset

        return self.queryset.filter(nodo__parcela__finca__usuario=self.request.user)


class LecturaSensorViewSet(viewsets.ModelViewSet):
    queryset = LecturaSensor.objects.all()
    serializer_class = LecturaSensorSerializer
    permission_classes = [IsUsuarioConRolActivoOrAdministradorWrite]

    def get_queryset(self):
        if usuario_ve_todo(self.request.user):
            return self.queryset

        return self.queryset.filter(sensor__nodo__parcela__finca__usuario=self.request.user)

    @action(detail=False, methods=['get'], url_path='latest-mqtt')
    def latest_mqtt(self, request):
        sensor_id = request.query_params.get('sensor_id')
        queryset = self.get_queryset().filter(observacion__icontains='MQTT')
        if sensor_id:
            queryset = queryset.filter(sensor_id=sensor_id)

        lectura = leer_lectura_mqtt(timeout=4)
        if lectura:
            queryset = self.get_queryset().filter(observacion__icontains='MQTT')
            if sensor_id:
                queryset = queryset.filter(sensor_id=sensor_id)

        latest = queryset.order_by('-fecha_hora').first()
        fresh_from_db = latest and latest.fecha_hora >= timezone.now() - timedelta(minutes=2)
        if latest and (lectura or fresh_from_db):
            return Response(self.get_serializer(latest).data)

        return Response({
            'mensaje': 'No se recibieron lecturas MQTT recientes para este sensor.',
            'mqtt': mqtt_status(),
        })


class ActuadorViewSet(viewsets.ModelViewSet):
    queryset = Actuador.objects.all()
    serializer_class = ActuadorSerializer
    permission_classes = [IsUsuarioConRolActivoOrAdministradorWrite]

    def get_queryset(self):
        if usuario_ve_todo(self.request.user):
            return self.queryset

        return self.queryset.filter(nodo__parcela__finca__usuario=self.request.user)
