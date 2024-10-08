# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-07 07:07
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.core.management import call_command
import zlib
from ledger.accounts.models import Profile

def generate_hash_oscar_address(address):
    fields = [address.line1, address.line2, address.line3,
              address.line4, address.state, address.country, address.postcode]

    fields = [str(f).strip() for f in fields if f]

    summary = u', '.join(fields)

    return zlib.crc32(summary.strip().upper().encode('UTF8'))

def generate_hash_postal_address(address):
    fields = [address.line1, address.line2, address.line3,
              address.locality, address.state, address.country, address.postcode]

    fields = [str(f).strip() for f in fields if f]

    summary = u', '.join(fields)

    return zlib.crc32(summary.strip().upper().encode('UTF8'))

def pre_save(instance, apps):
    UserAddress = apps.get_model('address', 'UserAddress')
    Address = apps.get_model('accounts', 'Address')
    Country = apps.get_model('address', 'Country')
    check_address = UserAddress(
        line1 = instance.line1,
        line2 = instance.line2,
        line3 = instance.line3,
        line4 = instance.locality,
        state = instance.state,
        postcode = instance.postcode,
        country = Country.objects.get(iso_3166_1_a2=instance.country),
        user = instance.user
    )
    original_instance = Address.objects.get(pk=instance.pk)
    if original_instance.oscar_address is None:
        try:
            check_address = UserAddress.objects.get(hash=generate_hash_oscar_address(check_address),user=check_address.user)
        except UserAddress.DoesNotExist:
            check_address.hash=generate_hash_oscar_address(check_address)
            check_address.save()
    return check_address

def update_profile_postal_address_user(apps, schema_editor):
    # Required for updating each postal_address__user_id record
    Profile = apps.get_model('accounts', 'Profile')
    try:
        for p in Profile.objects.all():
            p.postal_address.user = p.user
            p.postal_address.hash = generate_hash_postal_address(p.postal_address)
            p.postal_address.oscar_address = pre_save(p.postal_address, apps)
            p.postal_address.save()
    except Exception as e:
        raise e

def populate_countries(apps, schema_editor):
    call_command('oscar_populate_countries')

class Migration(migrations.Migration):

    dependencies = [
        # ('address', '0003_remove_useraddress_profile_address'),
        ('accounts', '0003_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='hash',
            field=models.CharField(db_index=True, editable=False, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='address',
            name='oscar_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile_addresses', to='address.UserAddress'),
        ),
        migrations.AddField(
            model_name='address',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile_adresses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RunPython(populate_countries),
        migrations.RunPython(update_profile_postal_address_user),
    ]

