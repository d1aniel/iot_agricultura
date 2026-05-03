from rest_framework import viewsets

from myapps.iot.models import Actuador, LecturaSensor, NodoIoT, Sensor
from myapps.iot.serializers import (
    ActuadorSerializer,
    LecturaSensorSerializer,
    NodoIoTSerializer,
    SensorSerializer,
)
from myapps.usuarios.permissions import IsUsuarioConRolActivo


class NodoIoTViewSet(viewsets.ModelViewSet):
    queryset = NodoIoT.objects.all()
    serializer_class = NodoIoTSerializer
    permission_classes = [IsUsuarioConRolActivo]


class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [IsUsuarioConRolActivo]


class LecturaSensorViewSet(viewsets.ModelViewSet):
    queryset = LecturaSensor.objects.all()
    serializer_class = LecturaSensorSerializer
    permission_classes = [IsUsuarioConRolActivo]


class ActuadorViewSet(viewsets.ModelViewSet):
    queryset = Actuador.objects.all()
    serializer_class = ActuadorSerializer
    permission_classes = [IsUsuarioConRolActivo]
