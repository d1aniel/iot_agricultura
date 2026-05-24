from rest_framework import serializers

from myapps.iot.models import Actuador, LecturaSensor, NodoIoT, Sensor


class NodoIoTSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodoIoT
        fields = '__all__'


class SensorSerializer(serializers.ModelSerializer):
    nodo_nombre = serializers.CharField(source='nodo.nombre', read_only=True)
    codigo_nodo = serializers.CharField(source='nodo.codigo_nodo', read_only=True)
    parcela_id = serializers.IntegerField(source='nodo.parcela_id', read_only=True)
    finca_id = serializers.IntegerField(source='nodo.parcela.finca_id', read_only=True)
    parcela_nombre = serializers.CharField(source='nodo.parcela.nombre', read_only=True)
    finca_nombre = serializers.CharField(source='nodo.parcela.finca.nombre', read_only=True)

    class Meta:
        model = Sensor
        fields = (
            'id',
            'nodo',
            'nodo_nombre',
            'codigo_nodo',
            'parcela_id',
            'finca_id',
            'parcela_nombre',
            'finca_nombre',
            'nombre',
            'tipo_sensor',
            'modelo',
            'unidad_medida',
            'pin_conexion',
            'valor_minimo',
            'valor_maximo',
            'estado',
            'fecha_instalacion',
        )


class LecturaSensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = LecturaSensor
        fields = '__all__'


class ActuadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actuador
        fields = '__all__'
