# Generated manually for command choice metadata.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('riego', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comandoriego',
            name='comando',
            field=models.CharField(
                choices=[
                    ('ENCENDER', 'Encender'),
                    ('APAGAR', 'Apagar'),
                    ('AUTO', 'Automatico'),
                    ('REINICIAR', 'Reiniciar'),
                ],
                max_length=30,
            ),
        ),
    ]
