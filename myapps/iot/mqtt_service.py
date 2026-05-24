import json
import ssl
import threading
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.db import close_old_connections
from django.utils import timezone

from myapps.iot.models import Actuador, LecturaSensor, NodoIoT, Sensor
from myapps.riego.models import EstadoRiego

try:
    import paho.mqtt.client as mqtt
except ImportError:  # pragma: no cover - handled by dependency installation
    mqtt = None


_listener_started = False
_listener_lock = threading.Lock()


def mqtt_configured():
    return bool(settings.MQTT_ENABLED and settings.MQTT_BROKER_HOST and mqtt)


def build_client(client_id):
    client = mqtt.Client(client_id=client_id)
    if settings.MQTT_USERNAME:
        client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)
    return client


def start_listener_once():
    global _listener_started

    if not mqtt_configured():
        return

    with _listener_lock:
        if _listener_started:
            return
        _listener_started = True

    thread = threading.Thread(target=_run_listener, name='mqtt-iot-listener', daemon=True)
    thread.start()


def publish_control(command):
    if not mqtt_configured():
        return False

    client = build_client('django-riego-publisher')
    client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, keepalive=30)
    client.loop_start()
    result = client.publish(settings.MQTT_TOPIC_CONTROL, command, qos=1)
    result.wait_for_publish(timeout=5)
    client.loop_stop()
    client.disconnect()
    return result.is_published()


def _run_listener():
    client = build_client('django-riego-listener')
    client.on_connect = _on_connect
    client.on_message = _on_message
    client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, keepalive=60)
    client.loop_forever()


def _on_connect(client, userdata, flags, reason_code, properties=None):
    client.subscribe(settings.MQTT_TOPIC_DATOS, qos=1)


def _on_message(client, userdata, message):
    close_old_connections()
    try:
        payload = json.loads(message.payload.decode('utf-8'))
        guardar_lectura_mqtt(payload)
    except Exception as exc:
        print(f'Error procesando MQTT: {exc}')
    finally:
        close_old_connections()


def guardar_lectura_mqtt(payload):
    codigo_nodo = payload.get('codigo_nodo') or payload.get('nodo') or settings.MQTT_DEFAULT_NODE_CODE
    nodo = buscar_nodo(codigo_nodo)
    if not nodo:
        raise ValueError('No se encontro un nodo IoT para la lectura MQTT.')

    humedad = normalizar_decimal(payload.get('humedad'))
    if humedad is None:
        raise ValueError('La lectura MQTT no incluye humedad valida.')

    nodo.ultima_conexion = timezone.now()
    nodo.estado = 'ACTIVO'
    nodo.save(update_fields=['ultima_conexion', 'estado'])

    sensor = obtener_sensor_humedad(nodo)
    LecturaSensor.objects.create(
        sensor=sensor,
        valor=humedad,
        unidad_medida='%',
        calidad_dato='VALIDO',
        observacion='Lectura recibida por MQTT',
    )

    actualizar_estado_actuador(nodo, payload)


def buscar_nodo(codigo_nodo):
    if codigo_nodo:
        return NodoIoT.objects.filter(codigo_nodo=codigo_nodo).first()
    return NodoIoT.objects.order_by('id').first()


def obtener_sensor_humedad(nodo):
    sensor = Sensor.objects.filter(nodo=nodo, tipo_sensor='HUMEDAD_SUELO').first()
    if sensor:
        return sensor

    return Sensor.objects.create(
        nodo=nodo,
        nombre=f'Humedad suelo {nodo.codigo_nodo}',
        tipo_sensor='HUMEDAD_SUELO',
        modelo='Sensor capacitivo',
        unidad_medida='%',
        estado='ACTIVO',
    )


def actualizar_estado_actuador(nodo, payload):
    actuador = Actuador.objects.filter(nodo=nodo).first()
    if not actuador:
        return

    riego_activo = bool(int(payload.get('riego', 0)))
    modo_payload = str(payload.get('modo', 'AUTO')).upper()
    estado_actual = 'ENCENDIDO' if riego_activo else 'APAGADO'
    modo = 'MANUAL' if modo_payload in ('ON', 'OFF') else 'AUTOMATICO'

    actuador.estado_actual = estado_actual
    actuador.estado = 'ACTIVO'
    actuador.save(update_fields=['estado_actual', 'estado'])

    ultimo = EstadoRiego.objects.filter(actuador=actuador).order_by('-fecha_hora_inicio').first()
    if ultimo and ultimo.estado == estado_actual and ultimo.modo == modo:
        return

    EstadoRiego.objects.create(
        actuador=actuador,
        estado=estado_actual,
        modo=modo,
        motivo='Reporte MQTT ESP32',
    )


def normalizar_decimal(value):
    try:
        return Decimal(str(value)).quantize(Decimal('0.01'))
    except (InvalidOperation, TypeError, ValueError):
        return None
