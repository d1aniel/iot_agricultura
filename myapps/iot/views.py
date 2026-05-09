from rest_framework import viewsets

from myapps.iot.models import Actuador, LecturaSensor, NodoIoT, Sensor
from myapps.iot.serializers import (
    ActuadorSerializer,
    LecturaSensorSerializer,
    NodoIoTSerializer,
    SensorSerializer,
)
from myapps.usuarios.permissions import IsUsuarioConRolActivoOrAdministradorWrite


def usuario_ve_todo(user):
    return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))


class NodoIoTViewSet(viewsets.ModelViewSet):
    queryset = NodoIoT.objects.all()
    serializer_class = NodoIoTSerializer
    permission_classes = [IsUsuarioConRolActivoOrAdministradorWrite]

    def get_queryset(self):
        if usuario_ve_todo(self.request.user):
            return self.queryset

        return self.queryset.filter(parcela__finca__usuario=self.request.user)


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


class ActuadorViewSet(viewsets.ModelViewSet):
    queryset = Actuador.objects.all()
    serializer_class = ActuadorSerializer
    permission_classes = [IsUsuarioConRolActivoOrAdministradorWrite]

    def get_queryset(self):
        if usuario_ve_todo(self.request.user):
            return self.queryset

        return self.queryset.filter(nodo__parcela__finca__usuario=self.request.user)
