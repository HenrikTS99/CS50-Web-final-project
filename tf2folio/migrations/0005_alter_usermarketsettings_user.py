# Generated by Django 4.2.7 on 2024-02-09 13:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tf2folio', '0004_remove_user_market_settings_usermarketsettings_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermarketsettings',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='market_settings', to=settings.AUTH_USER_MODEL),
        ),
    ]
