# Generated by Django 4.2.7 on 2024-02-28 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tf2folio', '0008_remove_item_description_alter_item_quality'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='image_url',
            field=models.URLField(blank=True, max_length=600, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='item_name',
            field=models.CharField(max_length=500),
        ),
    ]
