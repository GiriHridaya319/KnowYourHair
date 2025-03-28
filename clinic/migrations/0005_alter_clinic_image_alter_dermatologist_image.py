# Generated by Django 5.1.5 on 2025-02-25 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0004_remove_dermatologist_specialization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clinic',
            name='image',
            field=models.ImageField(default='default.jpg', upload_to='clinics_images/'),
        ),
        migrations.AlterField(
            model_name='dermatologist',
            name='image',
            field=models.ImageField(default='default.jpg', upload_to='dermatologist_images/'),
        ),
    ]
