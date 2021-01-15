from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.views.generic.base import View, TemplateView
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError
from django.db import transaction
from reversion_compare.views import HistoryCompareDetailView

from datetime import datetime, timedelta

from feewaiver.helpers import is_internal
from feewaiver.forms import *
from django.core.management import call_command
import json
from decimal import Decimal
from feewaiver.serializers import (
        ParticipantsSerializer,
        ParkSerializer,
        CampGroundSerializer,
)
from feewaiver.models import (
        FeeWaiverVisit,
        Participants,
        Park,
        CampGround,
        FeeWaiver
)


class FeeWaiverHistoryCompareView(HistoryCompareDetailView):
    """
    View for reversion_compare
    """
    model = FeeWaiver
    template_name = 'feewaiver/reversion_history.html'


class InternalView(UserPassesTestMixin, TemplateView):
    template_name = 'feewaiver/dash/index.html'

    def test_func(self):
        return is_internal(self.request)

    def get_context_data(self, **kwargs):
        context = super(InternalView, self).get_context_data(**kwargs)
        context['dev'] = settings.DEV_STATIC
        context['dev_url'] = settings.DEV_STATIC_URL
        if hasattr(settings, 'DEV_APP_BUILD_URL') and settings.DEV_APP_BUILD_URL:
            context['app_build_url'] = settings.DEV_APP_BUILD_URL
        return context

class ExternalView(TemplateView):
    template_name = 'feewaiver/dash/index.html'

    def get_context_data(self, **kwargs):
        context = super(ExternalView, self).get_context_data(**kwargs)
        context['dev'] = settings.DEV_STATIC
        context['dev_url'] = settings.DEV_STATIC_URL
        if hasattr(settings, 'DEV_APP_BUILD_URL') and settings.DEV_APP_BUILD_URL:
            context['app_build_url'] = settings.DEV_APP_BUILD_URL
        return context


class FeeWaiverRoutingView(TemplateView):
    template_name = 'feewaiver/index.html'

    def get(self, *args, **kwargs):
        web_url = self.request.META.get('HTTP_HOST', None)
        # only send internal users to login page
        if self.request.user.is_authenticated():
            if is_internal(self.request):
                return redirect('internal')
        elif web_url and '-internal' in web_url:
            kwargs['form'] = LoginForm
            return super(FeeWaiverRoutingView, self).get(*args, **kwargs)
        else:
            return redirect('external')

class FeeWaiverContactView(TemplateView):
    template_name = 'feewaiver/contact.html'

class FeeWaiverFurtherInformationView(TemplateView):
    template_name = 'feewaiver/further_info.html'


class HelpView(LoginRequiredMixin, TemplateView):
    template_name = 'feewaiver/help.html'

    def get_context_data(self, **kwargs):
        context = super(HelpView, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated():
            application_type = kwargs.get('application_type', None)
            if kwargs.get('help_type', None)=='assessor':
                if is_internal(self.request):
                    qs = HelpPage.objects.filter(application_type__name__icontains=application_type, help_type=HelpPage.HELP_TEXT_INTERNAL).order_by('-version')
                    context['help'] = qs.first()
            else:
                qs = HelpPage.objects.filter(application_type__name__icontains=application_type, help_type=HelpPage.HELP_TEXT_EXTERNAL).order_by('-version')
                context['help'] = qs.first()
        return context


class ManagementCommandsView(LoginRequiredMixin, TemplateView):
    template_name = 'feewaiver/mgt-commands.html'

    def post(self, request):
        data = {}
        command_script = request.POST.get('script', None)
        if command_script:
            print ('running {}'.format(command_script))
            call_command(command_script)
            data.update({command_script: 'true'})

        return render(request, self.template_name, data)


class InternalFeeWaiverView(DetailView):
    model = FeeWaiver
    template_name = 'feewaiver/dash/index.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            if is_internal(self.request):
                return super(InternalFeeWaiverView, self).get(*args, **kwargs)


class FeeWaiverAdminDataView(ListView):

    def get(self, *args, **kwargs):
        response = None

        camping_choices = []
        for choice in FeeWaiverVisit.CAMPING_CHOICES:
            camping_choices.append({choice[0]: choice[1]})
        park_serializer = ParkSerializer(Park.objects.all(), many=True)
        participants_serializer = ParticipantsSerializer(Participants.objects.all(), many=True)
        response = JsonResponse({
            "parks_list": park_serializer.data,
            "participants_list": participants_serializer.data,
            "camping_choices": camping_choices,
            })
        return response

