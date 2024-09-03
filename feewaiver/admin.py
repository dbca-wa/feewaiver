from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from feewaiver.models import *
from feewaiver.main_models import SystemMaintenance, FeeWaiverWordTemplate
from ledger.accounts import admin as ledger_admin
from ledger.accounts.models import EmailUser
from copy import deepcopy
from feewaiver import forms
from feewaiver.utils import to_local_tz


@admin.register(FeeWaiverWordTemplate)
class FeeWaiverWordTemplateAdmin(admin.ModelAdmin):
    list_display = ('Version', '_file', 'description', 'Date', 'Time')
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['_file', 'description', 'Date', 'Time']
        else:
            return []

    def Version(self, obj):
        return obj.id

    def Date(self, obj):
        local_date = to_local_tz(obj.uploaded_date)
        return local_date.strftime('%d/%m/%Y')

    def Time(self, obj):
        local_date = to_local_tz(obj.uploaded_date)
        return local_date.strftime('%H:%M')


@admin.register(SystemMaintenance)
class SystemMaintenanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'start_date', 'end_date', 'duration']
    ordering = ('start_date',)
    readonly_fields = ('duration',)
    form = forms.SystemMaintenanceAdminForm


class FeeWaiverAdminSite(AdminSite):
    site_header = 'Fee Waiver Administration'
    site_title = 'Fee Waiver System'
    index_title = 'Fee Waiver System'

#feewaiver_admin_site = FeeWaiverAdminSite(name='feewaiveradmin')

admin.site.unregister(EmailUser) # because this base classAdmin alsready registered in ledger.accounts.admin
@admin.register(EmailUser)
class EmailUserAdmin(ledger_admin.EmailUserAdmin):
    """
    Overriding the EmailUserAdmin from ledger.accounts.admin, to remove is_superuser checkbox field on Admin page
    """

    def get_fieldsets(self, request, obj=None):
        """ Remove the is_superuser checkbox from the Admin page, if user is CommercialOperatorAdmin and NOT superuser """
        fieldsets = super(UserAdmin, self).get_fieldsets(request, obj)
        #if not obj:
        #    return fieldsets

        if request.user.is_superuser:
            return fieldsets

        # User is not a superuser, remove is_superuser checkbox
        fieldsets = deepcopy(fieldsets)
        for fieldset in fieldsets:
            if 'is_superuser' in fieldset[1]['fields']:
                if type(fieldset[1]['fields']) == tuple :
                    fieldset[1]['fields'] = list(fieldset[1]['fields'])
                fieldset[1]['fields'].remove('is_superuser')
                break

        return fieldsets


@admin.register(FeeWaiver)
class FeeWaiverAdmin(admin.ModelAdmin):
    list_display = ['id', 'lodgement_number', 'lodgement_date', 'fee_waiver_purpose', 'assigned_officer', 'finalised',]
    list_filter = ['finalised',]


@admin.register(ContactDetails)
class ContactDetailsAdmin(admin.ModelAdmin):
    list_display = ['id', 'organisation', 'contact_name', 'email', 'postal_address', 'suburb', 'state', 'postcode', 'phone',]


@admin.register(Participants)
class ParticipantsAdmin(admin.ModelAdmin):
    ordering = ('name',)


@admin.register(Park)
class ParkAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email_list', 'entrance_fee',]
    list_display_links = ['id', 'name',]
    list_filter = ['entrance_fee',]
    ordering = ('name',)


#@admin.register(CampGround)
#class CampGroundAdmin(admin.ModelAdmin):
 #   pass


@admin.register(AssessorsGroup)
class AssessorsGroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('members',)
    actions = None

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "members":
            kwargs["queryset"] = EmailUser.objects.filter(is_staff=True)
        return super(AssessorsGroupAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def has_add_permission(self, request):
        return True if AssessorsGroup.objects.count() == 0 else False

    def has_delete_permission(self, request, obj=None):
        return False 

@admin.register(ApproversGroup)
class ApproversGroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('members',)
    actions = None

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "members":
            kwargs["queryset"] = EmailUser.objects.filter(is_staff=True)
        return super(ApproversGroupAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def has_add_permission(self, request):
        return True if ApproversGroup.objects.count() == 0 else False

    def has_delete_permission(self, request, obj=None):
        return False 

