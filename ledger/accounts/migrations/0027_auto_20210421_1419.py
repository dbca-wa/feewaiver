# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-04-21 06:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0026_privatedocument'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailuser',
            name='identification2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='identification_document_2', to='accounts.PrivateDocument'),
        ),
        migrations.AddField(
            model_name='emailuser',
            name='senior_card2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='senior_card', to='accounts.PrivateDocument'),
        ),
        migrations.AlterField(
            model_name='privatedocument',
            name='file_group',
            field=models.IntegerField(blank=True, choices=[(1, 'Identification'), (2, 'Senior Card')], null=True),
        ),
    ]
