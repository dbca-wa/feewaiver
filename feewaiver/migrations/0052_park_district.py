# Generated by Django 5.0.9 on 2024-11-28 06:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feewaiver', '0051_region_district'),
    ]

    operations = [
        migrations.AddField(
            model_name='park',
            name='district',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='feewaiver.district'),
        ),
    ]
