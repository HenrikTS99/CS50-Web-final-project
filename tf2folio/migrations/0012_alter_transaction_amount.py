# Generated by Django 4.2.7 on 2023-12-15 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tf2folio', '0011_alter_transaction_currency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
