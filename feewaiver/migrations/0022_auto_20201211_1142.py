# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-12-11 03:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feewaiver', '0021_auto_20201210_1406'),
    ]

    operations = [
        migrations.RenameField(
            model_name='feewaiveruseraction',
            old_name='contact_details',
            new_name='fee_waiver',
        ),
    ]
