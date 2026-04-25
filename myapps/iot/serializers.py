from rest_framework import serializers

from myapps.iot.models import Actuador, LecturaSensor, NodoIoT, Sensor


class NodoIoTSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodoIoT
        fields = '__all__'


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = '__all__'


class LecturaSensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = LecturaSensor
        fields = '__all__'


class ActuadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actuador
        fields = '__all__'
