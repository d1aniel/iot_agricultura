import time

from django.core.management.base import BaseCommand
from django.db import OperationalError, connections


class Command(BaseCommand):
    help = 'Espera a que la base de datos acepte conexiones antes de continuar.'
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument('--timeout', type=int, default=90)
        parser.add_argument('--interval', type=int, default=3)

    def handle(self, *args, **options):
        timeout = options['timeout']
        interval = options['interval']
        deadline = time.monotonic() + timeout
        connection = connections['default']
        last_error = None

        while time.monotonic() < deadline:
            try:
                connection.close()
                connection.ensure_connection()
                self.stdout.write(self.style.SUCCESS('Base de datos disponible.'))
                return
            except OperationalError as exc:
                last_error = exc
                self.stdout.write(f'Esperando base de datos: {exc}')
                time.sleep(interval)

        raise OperationalError(
            f'No fue posible conectar con la base de datos despues de {timeout} segundos. '
            f'Ultimo error: {last_error}'
        )
