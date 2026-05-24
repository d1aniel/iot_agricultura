from django.apps import AppConfig
from django.conf import settings


class IotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapps.iot'

    def ready(self):
        if not settings.MQTT_ENABLED:
            return

        from myapps.iot.mqtt_service import start_listener_once

        start_listener_once()
