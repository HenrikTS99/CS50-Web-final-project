# Generated by Django 4.2.7 on 2024-02-28 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tf2folio', '0007_alter_item_owner_alter_transaction_owner_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='description',
        ),
        migrations.AlterField(
            model_name='item',
            name='quality',
            field=models.CharField(choices=[('unique', 'Unique'), ('strange', 'Strange'), ('vintage', 'Vintage'), ('unusual', 'Unusual'), ('genuine', 'Genuine'), ('decorated', 'Decorated'), ('haunted', 'Haunted'), ('collectors', "Collector's"), ('normal', 'Normal')], max_length=20),
        ),
    ]