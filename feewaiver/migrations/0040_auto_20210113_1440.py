# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-01-13 06:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feewaiver', '0039_remove_usersystemsettings_one_row_per_park'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='park',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='participants',
            options={'ordering': ['name'], 'verbose_name_plural': 'Participants'},
        ),
    ]
