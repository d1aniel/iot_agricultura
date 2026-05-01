# Generated manually for API authentication and 2FA.

import django.db.models.deletion
import django.utils.timezone
import secrets
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
        migrations.CreateModel(
            name='TwoFactorDevice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('secret', models.CharField(max_length=64)),
                ('confirmado', models.BooleanField(default=False)),
                ('fecha_creacion', models.DateTimeField(default=django.utils.timezone.now)),
                ('fecha_confirmacion', models.DateTimeField(blank=True, null=True)),
                ('ultimo_codigo_usado', models.CharField(blank=True, max_length=12, null=True)),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='dispositivo_2fa', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'dispositivo 2FA',
                'verbose_name_plural': 'dispositivos 2FA',
                'db_table': 'two_factor_device',
            },
        ),
        migrations.CreateModel(
            name='LoginChallenge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('challenge_id', models.CharField(default=secrets.token_urlsafe, max_length=64, unique=True)),
                ('fecha_creacion', models.DateTimeField(default=django.utils.timezone.now)),
                ('fecha_expiracion', models.DateTimeField()),
                ('direccion_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('usado', models.BooleanField(default=False)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='retos_login', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'reto de login',
                'verbose_name_plural': 'retos de login',
                'db_table': 'login_challenge',
            },
        ),
    ]
