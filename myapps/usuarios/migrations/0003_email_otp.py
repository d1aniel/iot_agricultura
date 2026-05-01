# Reserved migration kept for compatibility with deployed databases.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_auth_token_2fa'),
    ]

    operations = []
