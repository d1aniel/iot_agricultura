# Generated manually for API authentication.

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_hash', models.CharField(max_length=64, unique=True)),
                ('nombre_dispositivo', models.CharField(blank=True, max_length=120, null=True)),
                ('direccion_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('fecha_creacion', models.DateTimeField(default=django.utils.timezone.now)),
                ('ultimo_uso', models.DateTimeField(blank=True, null=True)),
                ('fecha_expiracion', models.DateTimeField()),
                ('revocado', models.BooleanField(default=False)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tokens_api', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'token de autenticacion',
                'verbose_name_plural': 'tokens de autenticacion',
                'db_table': 'auth_token_api',
            },
        ),
    ]
