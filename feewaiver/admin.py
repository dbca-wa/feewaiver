from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from feewaiver.models import *
from feewaiver.main_models import SystemMaintenance, FeeWaiverWordTemplate
from ledger.accounts import admin as ledger_admin
from ledger.accounts.models import EmailUser
from copy import deepcopy
from feewaiver import forms, settings
from feewaiver.utils import to_local_tz
from django.utils.safestring import mark_safe


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
        local_date = to_local_tz(settings.TIME_ZONE, obj.uploaded_date)
        return local_date.strftime('%d/%m/%Y')

    def Time(self, obj):
        local_date = to_local_tz(settings.TIME_ZONE, obj.uploaded_date)
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
    list_display_links = ['id', 'lodgement_number',]
    list_filter = ['finalised',]
    search_fields = ['id', 'lodgement_number',]


@admin.register(ContactDetails)
class ContactDetailsAdmin(admin.ModelAdmin):
    list_display = ['id', 'organisation', 'contact_name', 'email', 'postal_address', 'suburb', 'state', 'postcode', 'phone',]
    search_fields = ['id', 'organisation', 'contact_name', 'email', 'postal_address', 'suburb', 'state', 'postcode', 'phone',]


@admin.register(Participants)
class ParticipantsAdmin(admin.ModelAdmin):
    search_fields = ['name',]
    ordering = ('name',)


@admin.register(Park)
class ParkAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'get_district', 'get_email_list', 'entrance_fee',]
    list_display_links = ['id', 'name',]
    list_filter = ['entrance_fee', 'district',]
    search_fields = ['id', 'name', 'email_list',]
    ordering = ('name',)

    def get_district(self, obj):
        if obj.district:
            return mark_safe(f'<a href="/ledger/admin/feewaiver/district/{obj.district.id}/change/">{obj.district.name}</a>')
        return '---'
    get_district.short_description = 'District'

    def get_email_list(self, obj):
        return mark_safe('<br>'.join(obj.email_list.split(';')))
    get_email_list.short_description = 'Email List'


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name',]
    list_display_links = ['id', 'name',]
    search_fields = ['id', 'name',]
    ordering = ('name',)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'get_region']
    list_display_links = ['id', 'name',]
    list_filter = ['region',]
    search_fields = ['id', 'name', 'region']
    ordering = ('name', 'region')

    def get_region(self, obj):
        if obj.region:
            return mark_safe(f'<a href="/ledger/admin/feewaiver/region/{obj.region.id}/change/">{obj.region.name}</a>')
        return '---'
    get_region.short_description = 'Region'


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

