# Generated by Django 4.2.7 on 2024-01-25 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tf2folio', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='estimated_price',
        ),
        migrations.AlterField(
            model_name='value',
            name='transaction_method',
            field=models.CharField(choices=[('keys', 'Keys'), ('scm_funds', 'Steam Funds'), ('paypal', 'PayPal'), ('items', 'TF2 Items')], default=('keys', 'Keys'), max_length=30),
        ),
    ]
