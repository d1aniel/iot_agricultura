from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iot', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='actuador',
            name='caudal_galones_hora',
            field=models.DecimalField(decimal_places=2, default=40.00, max_digits=10),
        ),
    ]
