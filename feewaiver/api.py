import re
import traceback
import os

import json

import pytz
from ledger.settings_base import TIME_ZONE, DATABASES
from django.db.models import Q
from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework import viewsets, serializers, status, views
from rest_framework.decorators import detail_route, list_route, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from ledger.accounts.models import EmailUser
from datetime import datetime

from django.http import HttpResponse
from feewaiver import settings

from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from feewaiver.serializers import (
        ContactDetailsSerializer,
        FeeWaiverSerializer,
        FeeWaiverMinimalSerializer,
        ContactDetailsSaveSerializer,
        FeeWaiverSaveSerializer,
        FeeWaiverDTSerializer,
        FeeWaiverVisitSerializer,
        FeeWaiverVisitSaveSerializer,
        FeeWaiverLogEntrySerializer,
        FeeWaiverUserActionSerializer,
        ParticipantsSerializer,
        ParkSerializer,
        CampGroundSerializer,
        TemporaryDocumentCollectionSerializer,
)
from feewaiver.models import (
        ContactDetails,
        ContactDetailsDocument,
        FeeWaiver,
        FeeWaiverVisit,
        FeeWaiverLogEntry,
        FeeWaiverUserAction,
        Participants,
        Park,
        CampGround,
)
from feewaiver.helpers import is_internal, is_feewaiver_admin
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.pagination import PageNumberPagination
from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.renderers import DatatablesRenderer
from feewaiver.process_document import (
        process_generic_document,
        save_contact_details_document_obj,
        save_default_document_obj,
        )
import logging
from feewaiver.emails import (
        send_fee_waiver_received_notification,
        send_workflow_notification,
        #send_approver_notification,
        send_approval_notification,
        )
from feewaiver.main_decorators import basic_exception_handler
from feewaiver.main_models import TemporaryDocumentCollection
from feewaiver.process_document import save_document, cancel_document, delete_document
logger = logging.getLogger(__name__)


class GetEmptyList(views.APIView):
    renderer_classes = [JSONRenderer, ]

    def get(self, request, format=None):
        return Response([])


class FeeWaiverFilterBackend(DatatablesFilterBackend):
    """
    Custom filters
    """

    def filter_queryset(self, request, queryset, view):
        total_count = queryset.count()

        def get_choice(status, choices=FeeWaiver.PROCESSING_STATUS_CHOICES):
            for i in choices:
                if i[1]==status:
                    return i[0]
            return None

        processing_status = request.GET.get('processing_status')
        if processing_status and not processing_status.lower() == 'all':
            processing_status = get_choice(processing_status, FeeWaiver.PROCESSING_STATUS_CHOICES)
            queryset = queryset.filter(processing_status=processing_status)

        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(lodgement_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(lodgement_date__lte=date_to)

        getter = request.query_params.get
        fields = self.get_fields(getter)
        ordering = self.get_ordering(getter, fields)
        queryset = queryset.order_by(*ordering)
        if len(ordering):
            queryset = queryset.order_by(*ordering)

        setattr(view, '_datatables_total_count', total_count)
        return queryset

class FeeWaiverRenderer(DatatablesRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if 'view' in renderer_context and hasattr(renderer_context['view'], '_datatables_total_count'):
            data['recordsTotal'] = renderer_context['view']._datatables_total_count
        return super(FeeWaiverRenderer, self).render(data, accepted_media_type, renderer_context)

class FeeWaiverPaginatedViewSet(viewsets.ModelViewSet):
    filter_backends = (FeeWaiverFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    renderer_classes = (FeeWaiverRenderer,)
    queryset = FeeWaiver.objects.none()
    serializer_class = FeeWaiverDTSerializer
    page_size = 10

    def get_queryset(self):
        if is_internal(self.request):
            return FeeWaiver.objects.all()
        return Feewaiver.objects.none()

    @list_route(methods=['GET',])
    def feewaiver_internal(self, request, *args, **kwargs):
        """
        Used by the internal dashboard

        http://localhost:8499/api/proposal_paginated/proposal_paginated_internal/?format=datatables&draw=1&length=2
        """
        qs = self.get_queryset()
        qs = self.filter_queryset(qs)

        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = FeeWaiverDTSerializer(result_page, context={
            'request':request,
            }, many=True)
        return self.paginator.get_paginated_response(serializer.data)


class FeeWaiverViewSet(viewsets.ModelViewSet):
    queryset = FeeWaiver.objects.none()
    serializer_class = FeeWaiverMinimalSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return FeeWaiver.objects.all()
        return FeeWaiver.objects.none()

    @detail_route(methods=['POST'])
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def process_contact_details_document(self, request, *args, **kwargs):
        instance = self.get_object()
        returned_data = process_generic_document(request, instance.contact_details)
        if returned_data:
            return Response(returned_data)
        else:
            return Response()

    @detail_route(methods=['POST'])
    @renderer_classes((JSONRenderer,))
    def process_comms_log_document(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            returned_data = process_generic_document(request, instance, document_type='comms_log')
            if returned_data:
                return Response(returned_data)
            else:
                return Response()

        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


    @detail_route(methods=['GET',])
    def assign_request_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.assign_officer(request,request.user)
            serializer = FeeWaiverSerializer(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @list_route(methods=['GET',])
    def filter_list(self, request, *args, **kwargs):
        """ Used by the internal/external dashboard filters """
        feewaiver_status = []
        data = dict(
            feewaiver_status_choices = [i[1] for i in FeeWaiver.PROCESSING_STATUS_CHOICES],
        )
        return Response(data)

    @list_route(methods=['GET',])
    def camping_choices(self, request, *args, **kwargs):
        camping_choices = []
        for choice in FeeWaiverVisit.CAMPING_CHOICES:
            camping_choices.append({choice[0]: choice[1]})
        return Response(camping_choices)

    @detail_route(methods=['GET',])
    def action_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.action_logs.all()
            serializer = FeeWaiverUserActionSerializer(qs,many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['GET',])
    def comms_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.comms_logs.all()
            serializer = FeeWaiverLogEntrySerializer(qs,many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST',])
    @renderer_classes((JSONRenderer,))
    def add_comms_log(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                request.data['fee_waiver'] = u'{}'.format(instance.id)
                serializer = FeeWaiverLogEntrySerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                comms = serializer.save()
                # Save the files
                for f in request.FILES:
                    document = comms.documents.create()
                    document.name = str(request.FILES[f])
                    document._file = request.FILES[f]
                    document.save()
                # End Save Documents

                return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


    @detail_route(methods=['POST',])
    def assign_to(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            user_id = request.data.get('assigned_officer_id',None)
            user = None
            if not user_id:
                raise serializers.ValidationError('An assigned officer id is required')
            try:
                user = EmailUser.objects.get(id=user_id)
            except EmailUser.DoesNotExist:
                raise serializers.ValidationError('A user with the id passed in does not exist')
            instance.assign_officer(request,user)
            serializer = FeeWaiverSerializer(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['GET',])
    def unassign(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.unassign(request)
            serializer = FeeWaiverSerializer(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST',])
    def switch_status(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            status = request.data.get('status')
            approver_comment = request.data.get('approver_comment')
            if not status:
                raise serializers.ValidationError('Status is required')
            else:
                if not status in ['with_assessor','with_assessor_requirements','with_approver']:
                    raise serializers.ValidationError('The status provided is not allowed')
            instance.move_to_status(request,status, approver_comment)
            serializer_class = self.internal_serializer_class()
            serializer = serializer_class(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e,'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


    @detail_route(methods=['POST'])
    @renderer_classes((JSONRenderer,))
    def workflow_action(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                action = request.data.get("workflow_type")
                email_subject = request.data.get("email_subject")
                if action == 'propose_issue':
                    instance.propose_issue(request)
                if action == 'propose_concession':
                    instance.propose_concession(request)
                if action == 'propose_decline':
                    instance.propose_decline(request)
                if action == 'return_to_assessor':
                    instance.return_to_assessor(request)
                comms_log_id = request.data.get('comms_log_id')
                workflow_entry = None
                if comms_log_id and comms_log_id != 'null':
                    workflow_entry = instance.comms_logs.get(
                            id=comms_log_id)
                # send email
                send_workflow_notification(instance,request, action, email_subject, workflow_entry)
                return Response()

        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST'])
    @renderer_classes((JSONRenderer,))
    def log_visit_action(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                visit_issued = request.data.get('issued')
                visit_index = request.data.get('index')
                checked_unchecked = "checked" if visit_issued else "unchecked"
                # send email
                instance.log_user_action(
                    FeeWaiverUserAction.ACTION_VISIT_FLAG.format(
                        visit_index + 1, 
                        instance.lodgement_number, 
                        checked_unchecked, 
                        request.user.get_full_name()),
                    request)
                return Response()

        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST'])
    @renderer_classes((JSONRenderer,))
    def final_approval(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                action = request.data.get("approval_type")
                if action == 'issue':
                    instance.issue(request)
                    instance.generate_doc(request)
                    email_subject = "Entry Fee Waiver Request {} has been issued".format(instance.lodgement_number)
                    send_approval_notification(instance, request, action, email_subject)
                if action == 'issue_concession':
                    instance.issue_concession(request)
                    instance.generate_doc(request)
                    email_subject = "Concession issued for Entry Fee Waiver Request {}".format(instance.lodgement_number)
                    send_approval_notification(instance, request, action, email_subject)
                if action == 'decline':
                    instance.decline(request)
                    email_subject = "Entry Fee Waiver Request {} has been declined".format(instance.lodgement_number)
                    send_approval_notification(instance, request, action, email_subject)

                # send email
                #send_approver_notification(instance, request, action)
                return Response()

        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST'])
    @renderer_classes((JSONRenderer,))
    def assessor_save(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                contact_details_data = request.data.get('contact_details')
                contact_serializer = ContactDetailsSaveSerializer(instance.contact_details, data=contact_details_data)
                contact_serializer.is_valid(raise_exception=True)
                contact_details_obj = contact_serializer.save()

                fee_waiver_data = request.data.get('fee_waiver')
                waiver_serializer = FeeWaiverSaveSerializer(instance, data=fee_waiver_data)
                waiver_serializer.is_valid(raise_exception=True)
                fee_waiver_obj = waiver_serializer.save()

                visits_data = request.data.get('visits')
                for visit in visits_data:
                    visit_obj = FeeWaiverVisit.objects.get(id=visit['id'])
                    visit_serializer = FeeWaiverVisitSaveSerializer(visit_obj, data=visit)
                    visit_serializer.is_valid(raise_exception=True)
                    visit_obj = visit_serializer.save()
                    # add parks
                    parks_data = visit.get('selected_park_ids')
                    if parks_data:
                        # add new parks
                        for park_id in parks_data:
                            if park_id not in [str(v_id) for v_id in visit_obj.parks.all().values_list('id', flat=True)]:
                                visit_obj.parks.add(Park.objects.get(id=park_id))
                        # remove unchecked parks
                        for db_park_id in [str(v_id) for v_id in visit_obj.parks.all().values_list('id', flat=True)]:
                            if db_park_id not in parks_data:
                                visit_obj.parks.remove(Park.objects.get(id=db_park_id))
                    # add free parks
                    free_parks_data = visit.get('selected_free_park_ids')
                    if free_parks_data:
                        # add new free parks
                        for free_park_id in free_parks_data:
                            if free_park_id not in [str(v_id) for v_id in visit_obj.free_parks.all().values_list('id', flat=True)]:
                                visit_obj.free_parks.add(Park.objects.get(id=free_park_id))
                        # remove unchecked free parks
                        for db_free_park_id in [str(v_id) for v_id in visit_obj.free_parks.all().values_list('id', flat=True)]:
                            if db_free_park_id not in free_parks_data:
                                visit_obj.free_parks.remove(Park.objects.get(id=db_free_park_id))

                    ## add campgrounds
                    #campgrounds_data = visit.get('selected_campground_ids')
                    #if campgrounds_data:
                    #    # add new campgrounds
                    #    for campground_id in campgrounds_data:
                    #        if campground_id not in [str(c_id) for c_id in visit_obj.campgrounds.all().values_list('id', flat=True)]:
                    #            visit_obj.campgrounds.add(CampGround.objects.get(id=campground_id))
                    #    # remove unchecked campgrounds
                    #    for db_campground_id in [str(c_id) for c_id in visit_obj.campgrounds.all().values_list('id', flat=True)]:
                    #        if db_campground_id not in campgrounds_data:
                    #            visit_obj.campgrounds.remove(CampGround.objects.get(id=db_campground_id))

                instance.log_user_action(
                    FeeWaiverUserAction.ACTION_SAVE.format(instance.lodgement_number, request.user.get_full_name()),
                    request)
                return Response()
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['get'])
    @renderer_classes((JSONRenderer,))
    def feewaiver_contactdetails_pack(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            contact_serializer = ContactDetailsSerializer(instance.contact_details)
            waiver_serializer = FeeWaiverSerializer(instance, context={'request': request})
            return Response({
                "contact_details": contact_serializer.data,
                "fee_waiver": waiver_serializer.data,
                })
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                contact_details_data = request.data.get('contact_details')
                contact_serializer = ContactDetailsSerializer(data=contact_details_data)
                contact_serializer.is_valid(raise_exception=True)
                contact_details_obj = contact_serializer.save()

                fee_waiver_data = request.data.get('fee_waiver')
                fee_waiver_data.update({'contact_details_id': contact_details_obj.id})
                waiver_serializer = FeeWaiverSerializer(data=fee_waiver_data)
                waiver_serializer.is_valid(raise_exception=True)
                fee_waiver_obj = waiver_serializer.save()
                # add visits
                visits_data = request.data.get('visits')
                for visit in visits_data:
                    visit['fee_waiver_id'] = fee_waiver_obj.id
                    visit_serializer = FeeWaiverVisitSerializer(data=visit)
                    visit_serializer.is_valid(raise_exception=True)
                    visit_obj = visit_serializer.save()
                    # add parks
                    parks_data = visit.get('selected_park_ids')
                    if parks_data:
                        for park_id in parks_data:
                            visit_obj.parks.add(Park.objects.get(id=park_id))
                    # add free parks
                    free_parks_data = visit.get('selected_free_park_ids')
                    if free_parks_data:
                        for free_park_id in free_parks_data:
                            visit_obj.free_parks.add(Park.objects.get(id=free_park_id))
                    # add campgrounds
                    #campgrounds_data = visit.get('selected_campground_ids')
                    #if campgrounds_data:
                     #   for campground_id in campgrounds_data:
                      #      visit_obj.campgrounds.add(CampGround.objects.get(id=campground_id))
                # send email
                send_fee_waiver_received_notification(fee_waiver_obj,request)
                email_subject = "Fee Waiver {} has been submitted".format(fee_waiver_obj.lodgement_number)
                send_workflow_notification(fee_waiver_obj,request, "submit", email_subject)
                temporary_document_collection_id = request.data.get('temporary_document_collection_id')
                if temporary_document_collection_id:
                    temp_doc_collection, created = TemporaryDocumentCollection.objects.get_or_create(
                            id=temporary_document_collection_id)
                    if temp_doc_collection:
                        for doc in temp_doc_collection.documents.all():
                            save_default_document_obj(contact_details_obj, doc)
                        temp_doc_collection.delete()

                fee_waiver_obj.log_user_action(
                    FeeWaiverUserAction.ACTION_SUBMIT.format(fee_waiver_obj.lodgement_number))
                return Response(waiver_serializer.data)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class SearchKeywordsView(views.APIView):
    renderer_classes = [JSONRenderer,]
    def post(self,request, format=None):
        qs = []
        searchWords = request.data.get('searchKeywords')
        searchProposal = request.data.get('searchProposal')
        searchApproval = request.data.get('searchApproval')
        searchCompliance = request.data.get('searchCompliance')
        if searchWords:
            qs= searchKeyWords(searchWords, searchProposal, searchApproval, searchCompliance)
        serializer = SearchKeywordSerializer(qs, many=True)
        return Response(serializer.data)


class SearchReferenceView(views.APIView):
    renderer_classes = [JSONRenderer,]
    def post(self,request, format=None):
        try:
            qs = []
            reference_number = request.data.get('reference_number')
            if reference_number:
                qs= search_reference(reference_number)
            serializer = SearchReferenceSerializer(qs)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e,'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                print(e)
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class ParticipantsViewSet(viewsets.ModelViewSet):
    queryset = Participants.objects.none()
    serializer_class = ParticipantsSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request): #user.is_authenticated():
            return Participants.objects.all()
        return Participants.objects.none()

    @list_route(methods=['GET',])
    def participants_list(self, request, *args, **kwargs):
        serializer = ParticipantsSerializer(Participants.objects.all(), many=True)
        return Response(serializer.data)


class ParkViewSet(viewsets.ModelViewSet):
    queryset = Park.objects.none()
    serializer_class = ParkSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return Park.objects.all()
        return Park.objects.none()

    @list_route(methods=['GET',])
    def parks_list(self, request, *args, **kwargs):
        serializer = ParkSerializer(Park.objects.all(), many=True)
        return Response(serializer.data)


class CampGroundViewSet(viewsets.ModelViewSet):
    queryset = CampGround.objects.none()
    serializer_class = CampGroundSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return CampGround.objects.all()
        return CampGround.objects.none()

    @list_route(methods=['GET',])
    def campgrounds_list(self, request, *args, **kwargs):
        serializer = CampGroundSerializer(CampGround.objects.all(), many=True)
        return Response(serializer.data)


class TemporaryDocumentCollectionViewSet(viewsets.ModelViewSet):
    queryset = TemporaryDocumentCollection.objects.all()
    serializer_class = TemporaryDocumentCollectionSerializer

    def create(self, request, *args, **kwargs):
        print("create temp doc coll")
        print(request.data)
        try:
            with transaction.atomic():
                serializer = TemporaryDocumentCollectionSerializer(
                        data=request.data, 
                        )
                serializer.is_valid(raise_exception=True)
                if serializer.is_valid():
                    instance = serializer.save()
                    save_document(request, instance, comms_instance=None, document_type=None)

                    return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST'])
    @renderer_classes((JSONRenderer,))
    # Designed for uploading comms_log files within "create" modals when no parent entity instance yet exists
    # response returned to compliance_file.vue
    def process_temp_comms_log_document(self, request, *args, **kwargs):
        print("process_temp_comms_log_document")
        print(request.data)
        try:
            instance = self.get_object()
            action = request.data.get('action')
            #comms_instance = None

            if action == 'list':
                pass

            elif action == 'delete':
                delete_document(request, instance, comms_instance=None, document_type=None)

            elif action == 'cancel':
                cancel_document(request, instance, comms_instance=None, document_type=None)

            elif action == 'save':
                save_document(request, instance, comms_instance=None, document_type=None)

            returned_file_data = [dict(
                        file=d._file.url,
                        id=d.id,
                        name=d.name,
                        ) for d in instance.documents.all() if d._file]
            return Response({'filedata': returned_file_data})

        except Exception as e:
            print(traceback.print_exc())
            raise e

    @detail_route(methods=['POST'])
    @renderer_classes((JSONRenderer,))
    # Designed for uploading comms_log files within "create" modals when no parent entity instance yet exists
    # response returned to compliance_file.vue
    def process_temp_document(self, request, *args, **kwargs):
        print("process_temp_document")
        print(request.data)
        try:
            instance = self.get_object()
            action = request.data.get('action')

            if action == 'list':
                pass

            elif action == 'delete':
                delete_document(request, instance, comms_instance=None, document_type=None)

            elif action == 'cancel':
                cancel_document(request, instance, comms_instance=None, document_type=None)

            elif action == 'save':
                save_document(request, instance, comms_instance=None, document_type=None)

            returned_file_data = [dict(
                        file=d._file.url,
                        id=d.id,
                        name=d.name,
                        ) for d in instance.documents.all() if d._file]
            return Response({'filedata': returned_file_data})

        except Exception as e:
            print(traceback.print_exc())
            raise e

