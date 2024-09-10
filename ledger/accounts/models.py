from __future__ import unicode_literals

# import os
# import zlib
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
# from django.contrib.postgres.fields import JSONField
from django.db.models import JSONField
from django.db import models, transaction
# from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.dispatch import receiver
# from django.db.models import Q
# from django.db.models.signals import post_delete, pre_save, post_save
# from django.core.exceptions import ValidationError

# from reversion import revisions
# from reversion.models import Version
from django_countries.fields import CountryField

# from social_django.models import UserSocialAuth

from datetime import datetime, date

from ledger.accounts.signals import name_changed, post_clean
from ledger.accounts.utils import get_department_user_compact, in_dbca_domain
from ledger.address.models import UserAddress, Country
from django.conf import settings

from django.core.files.storage import FileSystemStorage

from reversion import revisions
from reversion.models import Version

import logging
logger = logging.getLogger('log')


class EmailUserManager(BaseUserManager):
    """A custom Manager for the EmailUser model.
    """
    use_in_migrations = True

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        """Creates and saves an EmailUser with the given email and password.
        """
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email).lower()
        if (EmailUser.objects.filter(email__iexact=email) or
            Profile.objects.filter(email__iexact=email) or
            EmailIdentity.objects.filter(email__iexact=email)):
            raise ValueError('This email is already in use')
        user = self.model(
            email=email, is_staff=is_staff, is_superuser=is_superuser)
        user.extra_data = extra_fields
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)


# @python_2_unicode_compatible
class Document(models.Model):
    name = models.CharField(max_length=100, blank=True,
                            verbose_name='name', help_text='')
    description = models.TextField(blank=True,
                                   verbose_name='description', help_text='')
    file = models.FileField(upload_to='%Y/%m/%d')
    uploaded_date = models.DateTimeField(auto_now_add=True)

    @property
    def path(self):
        return self.file.path

    @property
    def filename(self):
        return os.path.basename(self.path)

    def __str__(self):
        return self.name or self.filename

upload_storage = FileSystemStorage(location=settings.LEDGER_PRIVATE_MEDIA_ROOT, base_url=settings.LEDGER_PRIVATE_MEDIA_URL)

# @python_2_unicode_compatible
class PrivateDocument(models.Model):

    FILE_GROUP = (
        (1,'Identification'),
        (2,'Senior Card'),
    )

    upload = models.FileField(max_length=512, upload_to='uploads/%Y/%m/%d', storage=upload_storage)
    name = models.CharField(max_length=256)
    metadata = JSONField(null=True, blank=True)
    text_content = models.TextField(null=True, blank=True, editable=False)  # Text for indexing
    file_group = models.IntegerField(choices=FILE_GROUP, null=True, blank=True)
    file_group_ref_id = models.IntegerField(null=True, blank=True)
    extension = models.CharField(max_length=5, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    @property
    def file_url(self):
         if self.extension is None:
                self.extension = ''
         return settings.LEDGER_PRIVATE_MEDIA_URL+str(self.pk)+'-file'+self.extension

    def __str__(self):
        if self.file_group:
            return '{} ({})'.format(self.name, self.get_file_group_display())
        return self.name

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
    user = models.ForeignKey('EmailUser', related_name='profile_addresses', on_delete=models.CASCADE)
    oscar_address = models.ForeignKey(UserAddress, related_name='profile_addresses', on_delete=models.PROTECT)
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

    residential_address = models.ForeignKey(Address, null=True, blank=False, related_name='+', on_delete=models.SET_NULL)
    postal_address = models.ForeignKey(Address, null=True, blank=True, related_name='+', on_delete=models.SET_NULL)
    postal_same_as_residential = models.BooleanField(default=False) 
    billing_address = models.ForeignKey(Address, null=True, blank=True, related_name='+', on_delete=models.SET_NULL)
    billing_same_as_residential = models.BooleanField(default=False)

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


class EmailUserChangeLog(models.Model):
    emailuser = models.ForeignKey(EmailUser, related_name='change_log_email_user', blank=True, null=True, on_delete=models.SET_NULL)
    change_key = models.CharField(max_length=1024, blank=True, null=True)
    change_value = models.CharField(max_length=1024, blank=True, null=True)
    change_by = models.ForeignKey(EmailUser, related_name='change_log_request_user', blank=True, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        app_label = 'accounts'
        ordering = ['-created']


class RevisionedMixin(models.Model):
    """
    A model tracked by reversion through the save method.
    """
    def save(self, **kwargs):
        if kwargs.pop('no_revision', False):
            super(RevisionedMixin, self).save(**kwargs)
        else:
            with revisions.create_revision():
                if 'version_user' in kwargs:
                    revisions.set_user(kwargs.pop('version_user', None))
                if 'version_comment' in kwargs:
                    revisions.set_comment(kwargs.pop('version_comment', ''))
                super(RevisionedMixin, self).save(**kwargs)

    @property
    def created_date(self):
        #return revisions.get_for_object(self).last().revision.date_created
        return Version.objects.get_for_object(self).last().revision.date_created

    @property
    def modified_date(self):
        #return revisions.get_for_object(self).first().revision.date_created
        return Version.objects.get_for_object(self).first().revision.date_created

    class Meta:
        abstract = True



class Organisation(models.Model):
    """This model represents the details of a company or other organisation.
    Management of these objects will be delegated to 0+ EmailUsers.
    """
    name = models.CharField(max_length=128, unique=True)
    abn = models.CharField(max_length=50, null=True, blank=True, verbose_name='ABN')
    # TODO: business logic related to identification file upload/changes.
    identification = models.FileField(upload_to='%Y/%m/%d', null=True, blank=True)
    postal_address = models.ForeignKey('OrganisationAddress', related_name='org_postal_address', blank=True, null=True, on_delete=models.SET_NULL)
    billing_address = models.ForeignKey('OrganisationAddress', related_name='org_billing_address', blank=True, null=True, on_delete=models.SET_NULL)
    email = models.EmailField(blank=True, null=True,)
    trading_name = models.CharField(max_length=256, null=True, blank=True)

    def upload_identification(self, request):
        with transaction.atomic():
            self.identification = request.data.dict()['identification']
            self.save()

    def __str__(self):
        return self.name

class OrganisationAddress(BaseAddress):
    organisation = models.ForeignKey(Organisation, null=True,blank=True, related_name='adresses', on_delete=models.SET_NULL)
    class Meta:
        verbose_name_plural = 'organisation addresses'
        #unique_together = ('organisation','hash')


class EmailUserReport(models.Model):
    hash = models.TextField(primary_key=True)
    occurence = models.IntegerField()
    first_name = models.CharField(max_length=128, blank=False, verbose_name='Given name(s)')
    last_name = models.CharField(max_length=128, blank=False)
    dob = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=False,verbose_name="date of birth", help_text='')

    def __str__(self):
        return 'Given Name(s): {}, Last Name: {}, DOB: {}, Occurence: {}'.format(self.first_name,self.last_name,self.dob,self.occurence)

    class Meta:
        managed = False
        db_table = 'accounts_emailuser_report_v'


def update_emailuser_comms_log_filename(instance, filename):
    return 'emailusers/{}/communications/{}/{}'.format(instance.log_entry.emailuser.id,instance.id,filename)


class EmailIdentity(models.Model):
    """Table used for matching access email address with EmailUser.
    """
    user = models.ForeignKey('EmailUser', null=True, on_delete=models.SET_NULL)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


class Profile(RevisionedMixin):
    user = models.ForeignKey(EmailUser, verbose_name='User', related_name='profiles', on_delete=models.CASCADE)
    name = models.CharField('Display Name', max_length=100, help_text='e.g Personal, Work, University, etc')
    email = models.EmailField('Email')
    postal_address = models.ForeignKey(Address, verbose_name='Postal Address', on_delete=models.PROTECT, related_name='profiles')
    institution = models.CharField('Institution', max_length=200, blank=True, default='', help_text='e.g. Company Name, Tertiary Institution, Government Department, etc')

    @property
    def is_auth_identity(self):
        """
        Return True if the email is an email identity; otherwise return False.
        """
        if not self.email:
            return False

        if not hasattr(self, "_auth_identity"):
            self._auth_identity = EmailIdentity.objects.filter(user=self.user, email=self.email).exists()

        return self._auth_identity

    def clean(self):
        super(Profile, self).clean()
        self.email = self.email.lower() if self.email else self.email
        post_clean.send(sender=self.__class__, instance=self)

    def __str__(self):
        if len(self.name) > 0:
            return '{} ({})'.format(self.name, self.email)
        else:
            return '{}'.format(self.email)