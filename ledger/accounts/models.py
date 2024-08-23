from __future__ import unicode_literals

# import os
# import zlib

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.postgres.fields import JSONField
from django.db import models, IntegrityError, transaction
# from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.dispatch import receiver
# from django.db.models import Q
from django.db.models.signals import post_delete, pre_save, post_save
# from django.core.exceptions import ValidationError

# from reversion import revisions
# from reversion.models import Version
from django_countries.fields import CountryField

# from social_django.models import UserSocialAuth

from datetime import datetime, date

from ledger.accounts.signals import name_changed, post_clean
from ledger.accounts.utils import get_department_user_compact, in_dbca_domain
from ledger.address.models import UserAddress, Country
# from django.conf import settings

# from django.core.files.storage import FileSystemStorage

import logging
logger = logging.getLogger('log')


class BaseAddress(models.Model):
    """Generic address model, intended to provide billing and shipping
    addresses.
    Taken from django-oscar address AbstrastAddress class.
    """
    STATE_CHOICES = (
        ('ACT', 'ACT'),
        ('NSW', 'NSW'),
        ('NT', 'NT'),
        ('QLD', 'QLD'),
        ('SA', 'SA'),
        ('TAS', 'TAS'),
        ('VIC', 'VIC'),
        ('WA', 'WA')
    )

    # Addresses consist of 1+ lines, only the first of which is
    # required.
    line1 = models.CharField('Line 1', max_length=255)
    line2 = models.CharField('Line 2', max_length=255, blank=True)
    line3 = models.CharField('Line 3', max_length=255, blank=True)
    locality = models.CharField('Suburb / Town', max_length=255)
    state = models.CharField(max_length=255, default='WA', blank=True)
    country = CountryField(default='AU')
    postcode = models.CharField(max_length=10)
    # A field only used for searching addresses.
    search_text = models.TextField(editable=False)
    hash = models.CharField(max_length=255, db_index=True, editable=False)

    def __str__(self):
        return self.summary

#    def __unicode__(self):
#        return ''

    class Meta:
        abstract = True

    def clean(self):
        # Strip all whitespace
        for field in ['line1', 'line2', 'line3',
                      'locality', 'state']:
            if self.__dict__[field]:
                self.__dict__[field] = self.__dict__[field].strip()

    def save(self, *args, **kwargs):
        self._update_search_text()
        self.hash = self.generate_hash()
        super(BaseAddress, self).save(*args, **kwargs)

    def _update_search_text(self):
        search_fields = filter(
            bool, [self.line1, self.line2, self.line3, self.locality,
                   self.state, str(self.country.name), self.postcode])
        self.search_text = ' '.join(search_fields)

    @property
    def summary(self):
        """Returns a single string summary of the address, separating fields
        using commas.
        """
        return u', '.join(self.active_address_fields())

    # Helper methods
#    def active_address_fields(self):
#        """Return the non-empty components of the address.
#        """
#        fields = [self.line1, self.line2, self.line3,
#                  self.locality, self.state, self.country, self.postcode]
#        fields = [str(f).strip() for f in fields if f]
#        
#        return fields


    # Helper methods
    def active_address_fields(self):
        """Return the non-empty components of the address.
        """
        fields = [self.line1, self.line2, self.line3,
                  self.locality, self.state, self.country, self.postcode]
        #for f in fields:
        #    print unicode(f).encode('utf-8').decode('unicode-escape').strip()
        #fields = [str(f).strip() for f in fields if f]
        fields = [unicode_compatible(f).encode('utf-8').decode('unicode-escape').strip() for f in fields if f]
        
        return fields

    def join_fields(self, fields, separator=u', '):
        """Join a sequence of fields using the specified separator.
        """
        field_values = []
        for field in fields:
            value = getattr(self, field)
            field_values.append(value)
        return separator.join(filter(bool, field_values))

    def generate_hash(self):
        """
            Returns a hash of the address summary
        """
        return zlib.crc32(self.summary.strip().upper().encode('UTF8'))


class Address(BaseAddress):
    user = models.ForeignKey('EmailUser', related_name='profile_addresses')
    oscar_address = models.ForeignKey(UserAddress, related_name='profile_addresses')
    class Meta:
        verbose_name_plural = 'addresses'
        unique_together = ('user','hash')


class EmailUser(AbstractBaseUser, PermissionsMixin):
    """Custom authentication model for the ledger project.
    Password and email are required. Other fields are optional.
    """
    email = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=128, blank=False, verbose_name='Given name(s)')
    last_name = models.CharField(max_length=128, blank=False)

    legal_first_name = models.CharField(max_length=128, null=True, blank=True, verbose_name='Legal Given name(s)')
    legal_last_name = models.CharField(max_length=128, null=True, blank=True)

    is_staff = models.BooleanField(
        default=False,
        help_text='Designates whether the user can log into the admin site.',
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this user should be treated as active.'
                  'Unselect this instead of deleting ledger.accounts.',
    )
    date_joined = models.DateTimeField(default=timezone.now)

    TITLE_CHOICES = (
        ('Mr', 'Mr'),
        ('Miss', 'Miss'),
        ('Mrs', 'Mrs'),
        ('Ms', 'Ms'),
        ('Dr', 'Dr')
    )
    title = models.CharField(max_length=100, choices=TITLE_CHOICES, null=True, blank=True,
                             verbose_name='title', help_text='')
    dob = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=False,
                           verbose_name="date of birth", help_text='')
    legal_dob = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True,
                           verbose_name="Legal date of birth", help_text='')
    phone_number = models.CharField(max_length=50, null=True, blank=True,
                                    verbose_name="phone number", help_text='')
    position_title = models.CharField(max_length=100, null=True, blank=True,
                                    verbose_name="position title", help_text='Automatically synced from AD,  please contact service desk to update.')
    mobile_number = models.CharField(max_length=50, null=True, blank=True,
                                     verbose_name="mobile number", help_text='')
    fax_number = models.CharField(max_length=50, null=True, blank=True,
                                  verbose_name="fax number", help_text='')
    organisation = models.CharField(max_length=300, null=True, blank=True,
                                    verbose_name="organisation", help_text='organisation, institution or company')

    residential_address = models.ForeignKey(Address, null=True, blank=False, related_name='+')
    postal_address = models.ForeignKey(Address, null=True, blank=True, related_name='+')
    postal_same_as_residential = models.NullBooleanField(default=False) 
    billing_address = models.ForeignKey(Address, null=True, blank=True, related_name='+')
    billing_same_as_residential = models.NullBooleanField(default=False)

    identification = models.ForeignKey(Document, null=True, blank=True, on_delete=models.SET_NULL, related_name='identification_document')
    identification2 = models.ForeignKey(PrivateDocument, null=True, blank=True, on_delete=models.SET_NULL, related_name='identification_document_2')

    senior_card = models.ForeignKey(Document, null=True, blank=True, on_delete=models.SET_NULL, related_name='senior_card')
    senior_card2 = models.ForeignKey(PrivateDocument, null=True, blank=True, on_delete=models.SET_NULL, related_name='senior_card')

    character_flagged = models.BooleanField(default=False)

    character_comments = models.TextField(blank=True)

    documents = models.ManyToManyField(Document)
  
    manager_email=models.EmailField(unique=False, blank=True, null=True, verbose_name='Manager Email')
    manager_name=models.CharField(max_length=128, blank=True, null=True, verbose_name='Manager Name')

    extra_data = JSONField(default=dict)

    objects = EmailUserManager()
    USERNAME_FIELD = 'email'

    def __str__(self):
        if self.is_dummy_user:
            if self.organisation:
                return '{} {} ({})'.format(self.first_name, self.last_name, self.organisation)
            return '{} {}'.format(self.first_name, self.last_name)
        else:
            if self.organisation:
                return '{} ({})'.format(self.email, self.organisation)
            return '{}'.format(self.email)

    def clean(self):
        super(EmailUser, self).clean()
        self.email = self.email.lower() if self.email else self.email
        post_clean.send(sender=self.__class__, instance=self)

    def save(self, *args, **kwargs):

        if not self.email:
            self.email = self.get_dummy_email()
        elif in_dbca_domain(self):
            pass
            # checks and updates department user details from address book after every login
            # #####################
            # Disabled as this has been moved to a management cron job.
            ########################
            #user_details = get_department_user_compact(self.email)
            #if user_details:
            #    # check if keys can be found in ITAssets api - the response JSON sent by API may have have changed
            #    if 'telephone' not in user_details or 'mobile_phone' not in user_details or 'title' not in user_details or 'location' not in user_details:
            #        logger.warn('Cannot find user details in ITAssets api call for user {}'.format(self.email))

            #    # Only set the below fields if there is a value from address book (in ITAssets API). 
            #    # This will allow fields in EmailUser object to be:
            #    #   a. overridden whenever newer/updated fields (e.g. telephone number) are available in address book
            #    #   b. if value for the field in address book empty/null, a previous value entered by user will not be overwritten with null
            #    if user_details.get('telephone'):
            #        self.phone_number = user_details.get('telephone') 
            #    if user_details.get('mobile_phone'):
            #        self.mobile_number = user_details.get('mobile_phone')
            #    if user_details.get('title'):
            #        self.position_title = user_details.get('title')
            #    if user_details.get('location', {}).get('fax'):
            #        self.fax_number = user_details.get('location', {}).get('fax')

            #    self.is_staff = True

        self.email = self.email.lower()
        self.email = self.email.replace(" ", "")

        super(EmailUser, self).save(*args, **kwargs)

    def get_full_name(self):

        full_name = '{} {}'.format(self.first_name, self.last_name)
        if self.legal_first_name and self.legal_last_name:
            legal_first_name = ''
            legal_last_name = ''
            if len(self.legal_first_name) > 0:
                legal_first_name = self.legal_first_name
            if len(self.legal_last_name) > 0:
                legal_last_name = self.legal_last_name
            if len(legal_first_name) > 0:
                full_name = '{} {}'.format(legal_first_name, legal_last_name)
        
        return full_name

    def get_full_name_dob(self):
        full_name_dob = '{} {} ({})'.format(self.first_name, self.last_name, self.dob.strftime('%d/%m/%Y'))
        return full_name_dob.strip()

    def get_short_name(self):
        if self.first_name:
            return self.first_name.split(' ')[0]
        return self.email

    def upload_identification(self, request):
        with transaction.atomic():
            document = Document(file=request.data.dict()['identification'])
            document.save()
            self.identification = document
            self.save()

    def upload_identification2(self, request):
        with transaction.atomic():
            document = PrivateDocument(upload=request.data.dict()['identification2'])
            document.save()
            self.identification2 = document
            self.save()

    dummy_email_suffix = ".s058@ledger.dpaw.wa.gov.au"
    dummy_email_suffix_len = len(dummy_email_suffix)

    @property
    def is_dummy_user(self):
        return not self.email or self.email[-1 * self.dummy_email_suffix_len:] == self.dummy_email_suffix

    @property
    def dummy_email(self):
        if self.is_dummy_user:
            return self.email
        else:
            return None

    def get_dummy_email(self):
        # use timestamp plus first name, last name to generate a unique id.
        uid = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return "{}.{}.{}{}".format(self.first_name, self.last_name, uid, self.dummy_email_suffix)

    @property
    def username(self):
        return self.email

    @property
    def is_senior(self):
        """
        Test if the the user is a senior according to the rules of WA senior
        dob is before 1 July 1955; or
        dob is between 1 July 1955 and 30 June 1956 and age is 61 or older; or
        dob is between 1 July 1956 and 30 June 1957 and age is 62 or older; or
        dob is between 1 July 1957 and 30 June 1958 and age is 63 or older; or
        dob is between 1 July 1958 and 30 June 1959 and age is 64 or older; or
        dob is after 30 June 1959 and age is 65 or older

        :return:
        """
        return \
            self.dob < date(1955, 7, 1) or \
            ((date(1955, 7, 1) <= self.dob <= date(1956, 6, 30)) and self.age() >= 61) or \
            ((date(1956, 7, 1) <= self.dob <= date(1957, 6, 30)) and self.age() >= 62) or \
            ((date(1957, 7, 1) <= self.dob <= date(1958, 6, 30)) and self.age() >= 63) or \
            ((date(1958, 7, 1) <= self.dob <= date(1959, 6, 30)) and self.age() >= 64) or \
            (self.dob > date(1959, 6, 1) and self.age() >= 65)

    def age(self):
        if self.dob:
            today = date.today()
            # calculate age with the help of trick int(True) = 1 and int(False) = 0
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        else:
            return -1


    def upload_identification(self, request):
        with transaction.atomic():
            document = Document(file=request.data.dict()['identification'])
            document.save()
            self.identification = document
            self.save()


    def log_user_action(self, action, request=None):
        if request:
            return EmailUserAction.log_action(self, action, request.user)
        else:
            pass
