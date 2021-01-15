from django.conf import settings
from django.contrib import admin
from django.conf.urls import url, include
from django.conf.urls.static import static
from rest_framework import routers
#from feewaiver import views, users_api, api
from feewaiver import views, api

from ledger.urls import urlpatterns as ledger_patterns
from feewaiver.management.default_data_manager import DefaultDataManager
from feewaiver.utils import are_migrations_running

# API patterns
router = routers.DefaultRouter()
router.register(r'feewaivers',api.FeeWaiverViewSet)
router.register(r'feewaivers_paginated',api.FeeWaiverPaginatedViewSet)
router.register(r'participants',api.ParticipantsViewSet)
router.register(r'parks',api.ParkViewSet)
router.register(r'campgrounds',api.CampGroundViewSet)
router.register(r'temporary_document', api.TemporaryDocumentCollectionViewSet)

api_patterns = [
    #url(r'^api/profile$', users_api.GetProfile.as_view(), name='get-profile'),
    #url(r'^api/department_users$', users_api.DepartmentUserList.as_view(), name='department-users-list'),
    #url(r'^api/filtered_users$', users_api.UserListFilterView.as_view(), name='filtered_users'),
    url(r'^api/',include(router.urls)),
]

# URL Patterns
urlpatterns = [
    url(r'^ledger/admin/', admin.site.urls, name='ledger_admin'),
    url(r'', include(api_patterns)),
    url(r'^$', views.FeeWaiverRoutingView.as_view(), name='ds_home'),
    url(r'^contact/', views.FeeWaiverContactView.as_view(), name='ds_contact'),
    url(r'^admin_data/', views.FeeWaiverAdminDataView.as_view(), name='admin_data'),
    url(r'^further_info/', views.FeeWaiverFurtherInformationView.as_view(), name='ds_further_info'),
    url(r'^internal/', views.InternalView.as_view(), name='internal'),
    url(r'^external/', views.ExternalView.as_view(), name='external'),
    url(r'^account/$', views.ExternalView.as_view(), name='manage-account'),
    url(r'^profiles/', views.ExternalView.as_view(), name='manage-profiles'),
    url(r'^help/(?P<application_type>[^/]+)/(?P<help_type>[^/]+)/$', views.HelpView.as_view(), name='help'),
    url(r'^mgt-commands/$', views.ManagementCommandsView.as_view(), name='mgt-commands'),
    url(r'^internal/fee_waiver/(?P<feewaiver_pk>\d+)/$', views.InternalFeeWaiverView.as_view(), name='internal-feewaiver-detail'),
    url(r'^history/fee_waiver/(?P<pk>\d+)/$', views.FeeWaiverHistoryCompareView.as_view(), name='feewaiver_history'),
] + ledger_patterns

if settings.DEBUG:  # Serve media locally in development.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.SHOW_DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns = [
        url('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns


if not are_migrations_running():
    DefaultDataManager()

