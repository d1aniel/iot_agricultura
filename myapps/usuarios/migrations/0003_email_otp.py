# Generated manually for email OTP challenges.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_auth_token_2fa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='twofactordevice',
            name='secret',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='loginchallenge',
            name='codigo_hash',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='loginchallenge',
            name='proposito',
            field=models.CharField(choices=[('LOGIN', 'Inicio de sesion'), ('ACTIVAR_2FA', 'Activar 2FA'), ('DESACTIVAR_2FA', 'Desactivar 2FA')], default='LOGIN', max_length=30),
        ),
    ]
