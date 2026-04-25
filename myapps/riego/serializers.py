from rest_framework import serializers

from myapps.riego.models import ComandoRiego, EstadoRiego, ReglaRiegoAutomatico, RespuestaComando


class EstadoRiegoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoRiego
        fields = '__all__'


class ReglaRiegoAutomaticoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReglaRiegoAutomatico
        fields = '__all__'


class ComandoRiegoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComandoRiego
        fields = '__all__'


class ComandoManualSerializer(serializers.Serializer):
    actuador_id = serializers.IntegerField()


class RespuestaComandoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestaComando
        fields = '__all__'
