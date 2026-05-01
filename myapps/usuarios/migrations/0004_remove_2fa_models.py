from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0003_email_otp'),
    ]

    operations = [
        migrations.RunSQL(
            sql='DROP TABLE IF EXISTS login_challenge',
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql='DROP TABLE IF EXISTS two_factor_device',
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
