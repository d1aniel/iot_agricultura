from rest_framework import serializers

from myapps.sistema.models import AlertaSistema, AuditoriaSistema


class AlertaSistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertaSistema
        fields = '__all__'


class AuditoriaSistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditoriaSistema
        fields = '__all__'
