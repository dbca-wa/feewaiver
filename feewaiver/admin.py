from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from feewaiver.models import *
from feewaiver.main_models import GlobalSettings, SystemMaintenance
from ledger.accounts import admin as ledger_admin
from ledger.accounts.models import EmailUser
from copy import deepcopy
from feewaiver import forms


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
    pass


@admin.register(ContactDetails)
class ContactDetailsAdmin(admin.ModelAdmin):
    pass


@admin.register(Participants)
class ParticipantsAdmin(admin.ModelAdmin):
    ordering = ('name',)


@admin.register(Park)
class ParkAdmin(admin.ModelAdmin):
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


@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    def get_fields(self, request, obj=None):
        if obj.key == GlobalSettings.KEY_FEEWAIVER_TEMPLATE_FILE:
            return ['key', '_file',]
        else:
            return ['key', 'value',]

    def get_readonly_fields(self, request, obj=None):
        return ['key',]

    list_display = ['key', 'value', '_file',]
    ordering = ('key',)


