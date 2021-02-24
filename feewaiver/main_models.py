from __future__ import unicode_literals
import os

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.utils.encoding import python_2_unicode_compatible
from django.core.exceptions import ValidationError
from ledger.accounts.models import EmailUser, RevisionedMixin
from django.contrib.postgres.fields.jsonb import JSONField
from datetime import datetime


class UserSystemSettings(models.Model):
    user = models.OneToOneField(EmailUser, related_name='system_settings')

    class Meta:
        app_label = 'feewaiver'
        verbose_name_plural = "User System Settings"


@python_2_unicode_compatible
class UserAction(models.Model):
    who = models.ForeignKey(EmailUser, null=False, blank=False)
    when = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    what = models.TextField(blank=False)

    def __str__(self):
        return "{what} ({who} at {when})".format(
            what=self.what,
            who=self.who,
            when=self.when
        )

    class Meta:
        abstract = True
        app_label = 'feewaiver'


class CommunicationsLogEntry(models.Model):
    TYPE_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone Call'),
        ('mail', 'Mail'),
        ('person', 'In Person'),
        ('onhold', 'On Hold'),
        ('onhold_remove', 'Remove On Hold'),
        ('with_qaofficer', 'With QA Officer'),
        ('with_qaofficer_completed', 'QA Officer Completed'),
        ('referral_complete','Referral Completed'),
    ]
    DEFAULT_TYPE = TYPE_CHOICES[0][0]

    to = models.TextField(blank=True, verbose_name="To")
    fromm = models.CharField(max_length=200, blank=True, verbose_name="From")
    cc = models.TextField(blank=True, verbose_name="cc")

    type = models.CharField(max_length=35, choices=TYPE_CHOICES, default=DEFAULT_TYPE)
    reference = models.CharField(max_length=100, blank=True)
    subject = models.CharField(max_length=200, blank=True, verbose_name="Subject / Description")
    text = models.TextField(blank=True)

    customer = models.ForeignKey(EmailUser, null=True, related_name='+')
    staff = models.ForeignKey(EmailUser, null=True, related_name='+')

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    class Meta:
        app_label = 'feewaiver'


@python_2_unicode_compatible
class Document(models.Model):
    name = models.CharField(max_length=255, blank=True,
                            verbose_name='name', help_text='')
    description = models.TextField(blank=True,
                                   verbose_name='description', help_text='')
    uploaded_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'feewaiver'
        abstract = True

    @property
    def path(self):
        #comment above line to fix the error "The '_file' attribute has no file associated with it." when adding comms log entry.
        if self._file:
            return self._file.path
        else:
            return ''

    @property
    def filename(self):
        return os.path.basename(self.path)

    def __str__(self):
        return self.name or self.filename


def update_feewaiver_word_filename(instance, filename):
    cur_time = datetime.now().strftime('%Y%m%d_%H_%M') 
    new_filename = 'fee_waiver_template_{}'.format(cur_time)
    return 'feewaiver_template/{}.docx'.format(new_filename)


class FeeWaiverWordTemplate(models.Model):
    _file = models.FileField(upload_to=update_feewaiver_word_filename, max_length=255)
    uploaded_date = models.DateTimeField(auto_now_add=True, editable=False)
    description = models.TextField(blank=True,
                                   verbose_name='description', help_text='')

    class Meta:
        app_label = 'feewaiver'
        verbose_name_plural = 'Fee Waiver Templates'
        ordering = ['-id']

    def __str__(self):
        return "Version: {}, {}".format(self.id, self._file.name)


@python_2_unicode_compatible
class SystemMaintenance(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def duration(self):
        """ Duration of system maintenance (in mins) """
        return int( (self.end_date - self.start_date).total_seconds()/60.) if self.end_date and self.start_date else ''
    duration.short_description = 'Duration (mins)'

    class Meta:
        app_label = 'feewaiver'
        verbose_name_plural = "System maintenance"

    def __str__(self):
        return 'System Maintenance: {} ({}) - starting {}, ending {}'.format(self.name, self.description, self.start_date, self.end_date)


class TemporaryDocumentCollection(models.Model):

    class Meta:
        app_label = 'feewaiver'


class TemporaryDocument(Document):
    temp_document_collection = models.ForeignKey(
        TemporaryDocumentCollection,
        related_name='documents')
    _file = models.FileField(max_length=255)

    class Meta:
        app_label = 'feewaiver'

import reversion
reversion.register(UserAction)
reversion.register(CommunicationsLogEntry)
reversion.register(Document)
reversion.register(SystemMaintenance)

