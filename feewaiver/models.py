from django.db import models
from feewaiver.main_models import CommunicationsLogEntry, UserAction, Document
from ledger.accounts.models import EmailUser, RevisionedMixin
from django.contrib.postgres.fields import ArrayField
from feewaiver.exceptions import FeeWaiverNotAuthorized
from django.db import transaction
from feewaiver.doctopdf import create_feewaiver_pdf_contents
from django.core.files.base import ContentFile


def update_feewaiver_doc_filename(instance, filename):
    return 'feewaiver/{}/documents/{}'.format(instance.feewaiver.id,filename)


class Participants(models.Model):
    name = models.CharField(max_length=256, blank=True, default='')

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'feewaiver'
        verbose_name_plural = 'Participants'
        ordering = ['name']


class Park(models.Model):
    name = models.CharField(max_length=256, blank=True, default='')
    email_list = models.CharField(max_length=256, blank=True, null=True, help_text='email addresses should be separated by semi-colons')
    entrance_fee = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'feewaiver'
        ordering = ['name']


class CampGround(models.Model):
    name = models.CharField(max_length=256, blank=True, default='')
    park = models.ForeignKey(Park, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'feewaiver'


class ContactDetails(RevisionedMixin):
    participants = models.ForeignKey(Participants, null=True, blank=True)
    organisation = models.CharField(max_length=256, blank=True, null=True)
    organisation_description = models.TextField(blank=True)
    contact_name = models.CharField(max_length=256, blank=True, null=True)
    postal_address = models.CharField(max_length=256, blank=True, null=True)
    suburb = models.CharField(max_length=256, blank=True, null=True)
    state = models.CharField(max_length=10, blank=True, null=True)
    postcode = models.CharField(max_length=10, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField()
    email_confirmation = models.EmailField()
    organisation_description = models.TextField(blank=True)

    def __str__(self):
        return 'Organisation: {}, Contact: {}'.format(self.organisation, self.contact_name)

    class Meta:
        app_label = 'feewaiver'
        verbose_name_plural = 'Contact Details'


class FeeWaiver(RevisionedMixin):
    PROCESSING_STATUS_WITH_ASSESSOR = 'with_assessor'
    PROCESSING_STATUS_WITH_APPROVER = 'with_approver'
    PROCESSING_STATUS_ISSUED = 'issued'
    PROCESSING_STATUS_CONCESSION = 'concession'
    PROCESSING_STATUS_DECLINED = 'declined'
    PROCESSING_STATUS_CHOICES = (
                                 (PROCESSING_STATUS_WITH_ASSESSOR, 'With Assessor'),
                                 (PROCESSING_STATUS_WITH_APPROVER, 'With Approver'),
                                 (PROCESSING_STATUS_ISSUED, 'Issued Fee Waiver'),
                                 (PROCESSING_STATUS_CONCESSION, 'Issued Concession'),
                                 (PROCESSING_STATUS_DECLINED, 'Declined'),
                                 )

    processing_status = models.CharField('Processing Status', max_length=30, choices=PROCESSING_STATUS_CHOICES,
                                         default=PROCESSING_STATUS_CHOICES[0][0])
    PROPOSED_STATUS_ISSUE = 'issue'
    PROPOSED_STATUS_CONCESSION = 'concession'
    PROPOSED_STATUS_DECLINE = 'decline'
    PROPOSED_STATUS_CHOICES = (
            (PROPOSED_STATUS_ISSUE, 'Fee Waiver'),
            (PROPOSED_STATUS_CONCESSION, 'Concession'),
            (PROPOSED_STATUS_DECLINE, 'Decline'),
                                 )
    proposed_status = models.CharField('Proposed Status', max_length=30, choices=PROPOSED_STATUS_CHOICES, null=True)
    lodgement_number = models.CharField(max_length=12, blank=True, default='')
    lodgement_date = models.DateTimeField(auto_now_add=True)
    contact_details = models.OneToOneField(ContactDetails, related_name="fee_waiver")
    fee_waiver_purpose = models.TextField(blank=True)
    assigned_officer = models.ForeignKey(EmailUser, blank=True, null=True, related_name='feewaiver_assigned', on_delete=models.SET_NULL)
    comments_to_applicant = models.TextField(blank=True)

    def __str__(self):
        return self.lodgement_number

    class Meta:
        app_label = 'feewaiver'

    def propose_issue(self, request):
        self.proposed_status = self.PROPOSED_STATUS_ISSUE
        self.move_to_approver(request)
        self.log_user_action(
            FeeWaiverUserAction.ACTION_PROPOSED_ISSUE.format(self.lodgement_number), 
            request)

    def propose_concession(self, request):
        self.proposed_status = self.PROPOSED_STATUS_CONCESSION
        self.move_to_approver(request)
        self.log_user_action(
            FeeWaiverUserAction.ACTION_PROPOSED_CONCESSION.format(self.lodgement_number), 
            request)

    def propose_decline(self, request):
        self.proposed_status = self.PROPOSED_STATUS_DECLINE
        self.move_to_approver(request)
        self.log_user_action(
            FeeWaiverUserAction.ACTION_PROPOSED_DECLINE.format(self.lodgement_number), 
            request)

    def move_to_approver(self, request):
        self.assigned_officer = None
        self.processing_status = self.PROCESSING_STATUS_WITH_APPROVER
        self.save()

    def issue(self, request):
        self.assigned_officer = None
        self.processing_status = self.PROCESSING_STATUS_ISSUED
        self.log_user_action(
            FeeWaiverUserAction.ACTION_ISSUE.format(self.lodgement_number), 
            request)
        self.save()

    def issue_concession(self, request):
        self.assigned_officer = None
        self.processing_status = self.PROCESSING_STATUS_CONCESSION
        self.log_user_action(
            FeeWaiverUserAction.ACTION_CONCESSION.format(self.lodgement_number), 
            request)
        self.save()

    def decline(self, request):
        self.assigned_officer = None
        self.processing_status = self.PROCESSING_STATUS_DECLINED
        self.log_user_action(
            FeeWaiverUserAction.ACTION_DECLINE.format(self.lodgement_number), 
            request)
        self.save()

    def return_to_assessor(self, request):
        self.assigned_officer = None
        self.processing_status = self.PROCESSING_STATUS_WITH_ASSESSOR
        self.log_user_action(
            FeeWaiverUserAction.ACTION_RETURN_TO_ASSESSOR.format(self.lodgement_number), 
            request)
        self.save()

    def save(self, *args, **kwargs):
        super(FeeWaiver, self).save(*args,**kwargs)
        if self.lodgement_number == '':
            new_lodgment_id = 'EFWR{0:06d}'.format(self.pk)
            self.lodgement_number = new_lodgment_id
            self.save()

    @property
    def processing_status_display(self):
        return self.get_processing_status_display()

    @property
    def proposed_status_display(self):
        return self.get_proposed_status_display()

    @property
    def relevant_access_group(self):
        if self.processing_status == 'with_assessor':
            return AssessorsGroup.objects.first().members.all()
        elif self.processing_status == 'with_approver':
            return ApproversGroup.objects.first().members.all()
        else:
            return []

    def log_user_action(self, action, request=None):
        if request:
            return FeeWaiverUserAction.log_action(self, action, request.user)
        else:
            return FeeWaiverUserAction.log_action(self, action)

    def assign_officer(self,request,officer):
        with transaction.atomic():
            try:
                if not self.can_action(request.user):
                    raise exceptions.FeeWaiverNotAuthorized()
                if officer != self.assigned_officer:
                    self.assigned_officer = officer
                    self.save()
                    # Create a log entry for the feewaiver
                    self.log_user_action(FeeWaiverUserAction.ACTION_ASSIGN_TO_OFFICER.format(self.lodgement_number, '{}({})'.format(officer.get_full_name(), officer.email)),
                            request)
            except:
                raise

    def unassign(self,request):
        with transaction.atomic():
            try:
                if not self.can_action(request.user):
                    raise exceptions.FeeWaiverNotAuthorized()
                if self.assigned_officer:
                    self.assigned_officer = None
                    self.save()
                    # Create a log entry for the proposal
                    self.log_user_action(FeeWaiverUserAction.ACTION_UNASSIGN_OFFICER.format(self.lodgement_number), 
                            request)
            except:
                raise

    def can_action(self,user):
        return user in self.relevant_access_group

    def generate_doc(self, request):
        feewaiver_document = self.create_feewaiver_document(request)
        self.save(version_comment='Created Feewaiver PDF: {}'.format(feewaiver_document.name))

    def create_feewaiver_document(self, request):
        pdf_contents = create_feewaiver_pdf_contents(self, request)

        filename = 'feewaiver-{}.pdf'.format(self.lodgement_number)
        document = FeeWaiverDocument.objects.create(feewaiver=self, name=filename)
        document._file.save(filename, ContentFile(pdf_contents), save=True)

        return document

    @property
    def latest_feewaiver_document(self):
        url = ''
        if self.documents.order_by('-uploaded_date'):
            url = self.documents.order_by('-uploaded_date')[0]._file.url
        return url


class FeeWaiverDocument(Document):
    feewaiver = models.ForeignKey(FeeWaiver,related_name='documents')
    _file = models.FileField(upload_to=update_feewaiver_doc_filename)

    class Meta:
        app_label = 'feewaiver'



class FeeWaiverVisit(RevisionedMixin):
    fee_waiver = models.ForeignKey(FeeWaiver, related_name="visit")
    description = models.TextField(blank=True)
    date_from = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=False,verbose_name="Date from", help_text='')
    date_to = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=False,verbose_name="Date to", help_text='')
    parks = models.ManyToManyField(Park)
    free_parks = models.ManyToManyField(Park, related_name="feewaiver_free_parks")
    campgrounds = models.ManyToManyField(CampGround)
    number_of_vehicles = models.IntegerField(default=0)
    number_of_participants = models.IntegerField(default=0)
    index = models.IntegerField(null=True)
    camping_requested = models.BooleanField(default=False)
    issued = models.BooleanField(default=True)
    AGE_CHOICES = (
        ('15', 'Under 15 yrs'),
        ('24', '15-24 yrs'),
        ('25', '25-39 yrs'),
        ('40', '40-59 yrs'),
        ('60', '60 yrs and over')
    )
    age_of_participants_array = ArrayField(
            models.CharField(max_length=100, choices=AGE_CHOICES),
            size=5,
            default=[],
            #null=True,
            )
    CAMPING_CHOICES = (
            ('', '-----'),
            ('child_rate', 'Adult camping fees at child rate'),
            ('full_waiver', 'Full camping waiver'),
            )
    camping_assessment = models.CharField(max_length=100, choices=CAMPING_CHOICES, default='',
                             verbose_name='Camping Assessment', help_text='')

    def __str__(self):
        return 'Fee Waiver: {}, Visit: {}'.format(self.fee_waiver.id, self.id)

    class Meta:
        app_label = 'feewaiver'


class ContactDetailsDocument(Document):
    contact_details = models.ForeignKey(ContactDetails,related_name='documents')
    _file = models.FileField(null=True)
    can_delete = models.BooleanField(default=True) # after initial submit prevent document from being deleted

    def delete(self):
        if self.can_delete:
            return super(ContactDetailsDocument, self).delete()
        logger.info('Cannot delete existing document object after Proposal has been submitted (including document submitted before Proposal pushback to status Draft): {}'.format(self.name))

    class Meta:
        app_label = 'feewaiver'


class FeeWaiverLogEntry(CommunicationsLogEntry):
    fee_waiver = models.ForeignKey(FeeWaiver, related_name='comms_logs')

    class Meta:
        app_label = 'feewaiver'


class FeeWaiverLogDocument(Document):
    log_entry = models.ForeignKey(FeeWaiverLogEntry,related_name='documents', null=True,)
    _file = models.FileField(null=True)

    class Meta:
        app_label = 'feewaiver'


class FeeWaiverUserAction(UserAction):
    ACTION_ASSIGN_TO_OFFICER = "Assign Fee Waiver {} to {}"
    ACTION_UNASSIGN_OFFICER = "Remove officer assignment from Fee Waiver {}"
    ACTION_PROPOSED_ISSUE = "Officer has proposed that Fee Waiver {} be issued"
    ACTION_PROPOSED_CONCESSION = "Officer has proposed that a concession be issued for Fee Waiver {}"
    ACTION_PROPOSED_DECLINE = "Officer has proposed that Fee Waiver {} be declined"
    ACTION_ISSUE = "Fee Waiver {} has been issued"
    ACTION_CONCESSION = "Fee Waiver {} has been issued with concession"
    ACTION_DECLINE = "Fee Waiver {} has been declined"
    ACTION_RETURN_TO_ASSESSOR = "Fee Waiver {} has been returned to Assessor"
    ACTION_SAVE = "Fee Waiver {} has been saved by {}"
    ACTION_SUBMIT = "Fee Waiver {} has been submitted"
    ACTION_VISIT_FLAG = "Visit {} for Fee Waiver {} has been {}"
    ACTION_DELETE_DOCUMENT = "Fee Waiver {} Contact Details document '{}' has been deleted"
    ACTION_SAVE_DOCUMENT = "Fee Waiver {} Contact Details document '{}' has been saved"

    class Meta:
        app_label = 'feewaiver'
        ordering = ('-when',)

    @classmethod
    def log_action(cls, fee_waiver, action, user=None):
        return cls.objects.create(
            fee_waiver=fee_waiver,
            who=user,
            what=str(action)
        )

    fee_waiver = models.ForeignKey(FeeWaiver, related_name='action_logs')
    who = models.ForeignKey(EmailUser, null=True, blank=True)


class AssessorsGroup(models.Model):
    members = models.ManyToManyField(EmailUser)

    def __str__(self):
        return 'Assessors Group'

    @property
    def all_members(self):
        all_members = []
        all_members.extend(self.members.all())
        member_ids = [m.id for m in self.members.all()]
        return all_members

    @property
    def filtered_members(self):
        return self.members.all()

    class Meta:
        app_label = 'feewaiver'
        verbose_name_plural = "Assessors group"


class ApproversGroup(models.Model):
    members = models.ManyToManyField(EmailUser)

    def __str__(self):
        return 'Approvers Group'

    @property
    def all_members(self):
        all_members = []
        all_members.extend(self.members.all())
        member_ids = [m.id for m in self.members.all()]
        return all_members

    @property
    def filtered_members(self):
        return self.members.all()

    class Meta:
        app_label = 'feewaiver'
        verbose_name_plural = "Approvers group"


import reversion
reversion.register(Participants)
reversion.register(Park)
reversion.register(ContactDetails, follow=['participants', 'documents'])
reversion.register(FeeWaiver, follow=['assigned_officer', 'visit', 'documents'])
reversion.register(ContactDetailsDocument)
reversion.register(FeeWaiverDocument)
reversion.register(FeeWaiverVisit, follow=['parks', 'free_parks'])
reversion.register(AssessorsGroup)
reversion.register(ApproversGroup)
reversion.register(EmailUser)
reversion.register(FeeWaiverLogEntry, follow=['documents',])
reversion.register(FeeWaiverLogDocument)
reversion.register(FeeWaiverUserAction)
