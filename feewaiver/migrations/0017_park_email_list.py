# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-12-08 07:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feewaiver', '0016_auto_20201208_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='park',
            name='email_list',
            field=models.CharField(blank=True, help_text='email addresses should be separated by semi-colons', max_length=256, null=True),
        ),
    ]