# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-01-19 06:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feewaiver', '0043_auto_20210119_1410'),
    ]

    operations = [
        migrations.DeleteModel(
            name='GlobalSettings',
        ),
    ]
