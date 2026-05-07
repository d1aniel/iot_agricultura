from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0004_remove_2fa_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuarioperfil',
            name='requiere_cambio_password',
            field=models.BooleanField(default=False),
        ),
    ]
