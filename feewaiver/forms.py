from django.contrib.auth import get_user_model
from django import forms
from feewaiver.main_models import SystemMaintenance
import pytz
from django.conf import settings
from datetime import datetime, timedelta


User = get_user_model()


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254)


class SystemMaintenanceAdminForm(forms.ModelForm):
    class Meta:
        model = SystemMaintenance
        fields = '__all__'

    def clean(self):
        cleaned_data = self.cleaned_data
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        try:
            latest_obj = SystemMaintenance.objects.exclude(id=self.instance.id).latest('start_date')
        except: 
            latest_obj = SystemMaintenance.objects.none()
        tz_local = pytz.timezone(settings.TIME_ZONE) #start_date.tzinfo
        tz_utc = pytz.timezone('utc') #latest_obj.start_date.tzinfo

        if latest_obj:
            latest_end_date = latest_obj.end_date.astimezone(tz=tz_local)
            if self.instance.id:
                if start_date < latest_end_date and start_date < self.instance.start_date.astimezone(tz_local):
                    raise forms.ValidationError('Start date cannot be before an existing records latest end_date. Start Date must be after {}'.format(latest_end_date.ctime()))
            else:
                if start_date < latest_end_date:
                    raise forms.ValidationError('Start date cannot be before an existing records latest end_date. Start Date must be after {}'.format(latest_end_date.ctime()))

        if self.instance.id:
            if start_date < datetime.now(tz=tz_local) - timedelta(minutes=5) and start_date < self.instance.start_date.astimezone(tz_local):
                raise forms.ValidationError('Start date cannot be edited to be further in the past')
        else:
            if start_date < datetime.now(tz=tz_local) - timedelta(minutes=5):
                raise forms.ValidationError('Start date cannot be in the past')

        if end_date < start_date:
            raise forms.ValidationError('End date cannot be before start date')

        super(SystemMaintenanceAdminForm, self).clean()
        return cleaned_data

