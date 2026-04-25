from rest_framework import viewsets

from myapps.sistema.models import AlertaSistema, AuditoriaSistema
from myapps.sistema.serializers import AlertaSistemaSerializer, AuditoriaSistemaSerializer


class AlertaSistemaViewSet(viewsets.ModelViewSet):
    queryset = AlertaSistema.objects.all()
    serializer_class = AlertaSistemaSerializer


class AuditoriaSistemaViewSet(viewsets.ModelViewSet):
    queryset = AuditoriaSistema.objects.all()
    serializer_class = AuditoriaSistemaSerializer
