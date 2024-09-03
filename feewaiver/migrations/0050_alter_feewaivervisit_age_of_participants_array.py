# Generated by Django 5.0.8 on 2024-09-03 06:06

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feewaiver', '0049_auto_20240829_1150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feewaivervisit',
            name='age_of_participants_array',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('15', 'Under 15 yrs'), ('24', '15-24 yrs'), ('25', '25-39 yrs'), ('40', '40-59 yrs'), ('60', '60 yrs and over')], max_length=100), default=list, size=5),
        ),
    ]