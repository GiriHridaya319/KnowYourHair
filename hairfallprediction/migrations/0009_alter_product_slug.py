# Generated by Django 5.1.5 on 2025-02-24 03:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hairfallprediction', '0008_alter_product_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(max_length=500, unique=True),
        ),
    ]
