from rest_framework import viewsets

from myapps.sistema.models import AlertaSistema, AuditoriaSistema
from myapps.sistema.serializers import AlertaSistemaSerializer, AuditoriaSistemaSerializer
from myapps.usuarios.permissions import IsAdministradorOrAuditor


class AlertaSistemaViewSet(viewsets.ModelViewSet):
    queryset = AlertaSistema.objects.all()
    serializer_class = AlertaSistemaSerializer
    permission_classes = [IsAdministradorOrAuditor]


class AuditoriaSistemaViewSet(viewsets.ModelViewSet):
    queryset = AuditoriaSistema.objects.all()
    serializer_class = AuditoriaSistemaSerializer
    permission_classes = [IsAdministradorOrAuditor]
