# Generated by Django 5.1.5 on 2025-02-19 19:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_rename_specialization_agent_role_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='profile',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='agent', to='user.profile'),
        ),
        migrations.AlterField(
            model_name='agent',
            name='role',
            field=models.CharField(blank=True, default='staff', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='profile',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='customer', to='user.profile'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='role',
            field=models.CharField(blank=True, default='customer', max_length=100, null=True),
        ),
    ]
