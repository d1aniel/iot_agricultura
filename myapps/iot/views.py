from rest_framework import viewsets

from myapps.iot.models import Actuador, LecturaSensor, NodoIoT, Sensor
from myapps.iot.serializers import (
    ActuadorSerializer,
    LecturaSensorSerializer,
    NodoIoTSerializer,
    SensorSerializer,
)


class NodoIoTViewSet(viewsets.ModelViewSet):
    queryset = NodoIoT.objects.all()
    serializer_class = NodoIoTSerializer


class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer


class LecturaSensorViewSet(viewsets.ModelViewSet):
    queryset = LecturaSensor.objects.all()
    serializer_class = LecturaSensorSerializer


class ActuadorViewSet(viewsets.ModelViewSet):
    queryset = Actuador.objects.all()
    serializer_class = ActuadorSerializer
