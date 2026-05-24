from django.apps import AppConfig
from django.conf import settings
import sys


class IotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapps.iot'

    def ready(self):
        if not settings.MQTT_ENABLED:
            return
        if any(command in sys.argv for command in ('check', 'collectstatic', 'makemigrations', 'migrate', 'shell', 'wait_for_db')):
            return

        from myapps.iot.mqtt_service import start_listener_once

        start_listener_once()
