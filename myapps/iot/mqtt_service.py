import json
import logging
import ssl
import threading
import uuid
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


logger = logging.getLogger(__name__)
_listener_started = False
_listener_lock = threading.Lock()
_last_payload = None
_last_saved_reading = None
_last_error = ''


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
        logger.warning('MQTT no configurado. enabled=%s host=%s paho=%s', settings.MQTT_ENABLED, settings.MQTT_BROKER_HOST, bool(mqtt))
        return

    with _listener_lock:
        if _listener_started:
            return
        _listener_started = True

    thread = threading.Thread(target=_run_listener, name='mqtt-iot-listener', daemon=True)
    thread.start()
    logger.info('Listener MQTT iniciado para topic %s', settings.MQTT_TOPIC_DATOS)


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


def leer_lectura_mqtt(timeout=4):
    if not mqtt_configured():
        set_last_error('MQTT no esta configurado.')
        return None

    event = threading.Event()
    result = {'lectura': None}

    def on_connect(client, userdata, flags, reason_code, properties=None):
        client.subscribe(settings.MQTT_TOPIC_DATOS, qos=1)
        logger.info('MQTT lectura bajo demanda conectado con codigo %s', reason_code)

    def on_message(client, userdata, message):
        close_old_connections()
        try:
            raw_payload = message.payload.decode('utf-8')
            logger.info('Mensaje MQTT bajo demanda en %s: %s', message.topic, raw_payload)
            payload = json.loads(raw_payload)
            set_last_payload(payload)
            lectura = guardar_lectura_mqtt(payload)
            set_last_saved_reading(lectura)
            result['lectura'] = lectura
        except Exception as exc:
            set_last_error(f'Error procesando MQTT bajo demanda: {exc}')
            logger.exception('Error procesando MQTT bajo demanda')
        finally:
            close_old_connections()
            event.set()

    client = build_client(f'django-riego-demand-{uuid.uuid4().hex[:10]}')
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, keepalive=30)
        client.loop_start()
        event.wait(timeout)
    except Exception as exc:
        set_last_error(f'Error leyendo MQTT bajo demanda: {exc}')
        logger.exception('Error leyendo MQTT bajo demanda')
    finally:
        client.loop_stop()
        client.disconnect()

    return result['lectura']


def _run_listener():
    client = build_client(f'django-riego-listener-{uuid.uuid4().hex[:10]}')
    client.on_connect = _on_connect
    client.on_message = _on_message
    try:
        client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, keepalive=60)
        client.loop_forever(retry_first_connection=True)
    except Exception as exc:
        set_last_error(f'Error listener MQTT: {exc}')
        logger.exception('Error ejecutando listener MQTT')


def _on_connect(client, userdata, flags, reason_code, properties=None):
    client.subscribe(settings.MQTT_TOPIC_DATOS, qos=1)
    logger.info('MQTT conectado con codigo %s. Suscrito a %s', reason_code, settings.MQTT_TOPIC_DATOS)


def _on_message(client, userdata, message):
    close_old_connections()
    try:
        raw_payload = message.payload.decode('utf-8')
        logger.info('Mensaje MQTT recibido en %s: %s', message.topic, raw_payload)
        payload = json.loads(raw_payload)
        set_last_payload(payload)
        lectura = guardar_lectura_mqtt(payload)
        set_last_saved_reading(lectura)
    except Exception as exc:
        set_last_error(f'Error procesando MQTT: {exc}')
        logger.exception('Error procesando MQTT')
    finally:
        close_old_connections()


def guardar_lectura_mqtt(payload):
    codigo_nodo = payload.get('codigo_nodo') or payload.get('nodo') or payload.get('codigo') or settings.MQTT_DEFAULT_NODE_CODE
    nodo = buscar_nodo(codigo_nodo)
    if not nodo:
        raise ValueError(f'No se encontro un nodo IoT para la lectura MQTT. codigo_nodo={codigo_nodo or "vacio"}')

    humedad = normalizar_decimal(payload.get('humedad'))
    if humedad is None:
        raise ValueError('La lectura MQTT no incluye humedad valida.')

    nodo.ultima_conexion = timezone.now()
    nodo.estado = 'ACTIVO'
    nodo.save(update_fields=['ultima_conexion', 'estado'])

    sensor = obtener_sensor_humedad(nodo)
    lectura = LecturaSensor.objects.create(
        sensor=sensor,
        valor=humedad,
        unidad_medida='%',
        calidad_dato='VALIDO',
        observacion='Lectura recibida por MQTT',
    )

    actualizar_estado_actuador(nodo, payload)
    logger.info('Lectura MQTT guardada. nodo=%s sensor=%s humedad=%s lectura=%s', nodo.codigo_nodo, sensor.id, humedad, lectura.id)
    return lectura


def buscar_nodo(codigo_nodo):
    if codigo_nodo:
        nodo = NodoIoT.objects.filter(codigo_nodo=codigo_nodo).first()
        if nodo:
            return nodo

    if NodoIoT.objects.count() == 1:
        return NodoIoT.objects.first()

    return None


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


def set_last_payload(payload):
    global _last_payload, _last_error
    _last_payload = payload
    _last_error = ''


def set_last_saved_reading(lectura):
    global _last_saved_reading, _last_error
    _last_saved_reading = {
        'id': lectura.id,
        'sensor_id': lectura.sensor_id,
        'valor': str(lectura.valor),
        'fecha_hora': lectura.fecha_hora.isoformat(),
    }
    _last_error = ''


def set_last_error(message):
    global _last_error
    _last_error = message


def mqtt_status():
    return {
        'enabled': settings.MQTT_ENABLED,
        'configured': mqtt_configured(),
        'listener_started': _listener_started,
        'topic_datos': settings.MQTT_TOPIC_DATOS,
        'topic_control': settings.MQTT_TOPIC_CONTROL,
        'default_node_code': settings.MQTT_DEFAULT_NODE_CODE,
        'last_payload': _last_payload,
        'last_saved_reading': _last_saved_reading,
        'last_error': _last_error,
    }
