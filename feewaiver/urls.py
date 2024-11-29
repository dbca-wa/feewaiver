from django.conf import settings
from django.contrib import admin
# from django.conf.urls import url, include
from django.urls import path, include, re_path
from django.conf.urls.static import static
from rest_framework import routers
#from feewaiver import views, users_api, api
from feewaiver import views, api

from ledger.urls import urlpatterns as ledger_patterns
from feewaiver.utils import are_migrations_running

# API patterns
router = routers.DefaultRouter()
router.include_root_view = settings.SHOW_ROOT_API
router.register(r'feewaivers',api.FeeWaiverViewSet)
router.register(r'feewaivers_paginated',api.FeeWaiverPaginatedViewSet, basename='feewaiver-paginated')
router.register(r'participants',api.ParticipantsViewSet)
router.register(r'parks',api.ParkViewSet)
router.register(r'campgrounds',api.CampGroundViewSet)
router.register(r'temporary_document', api.TemporaryDocumentCollectionViewSet)

api_patterns = [
    #url(r'^api/profile$', users_api.GetProfile.as_view(), name='get-profile'),
    #url(r'^api/department_users$', users_api.DepartmentUserList.as_view(), name='department-users-list'),
    #url(r'^api/filtered_users$', users_api.UserListFilterView.as_view(), name='filtered_users'),
    re_path(r'^api/',include(router.urls)),
]

# URL Patterns
urlpatterns = [
    re_path(r'^ledger/admin/', admin.site.urls, name='ledger_admin'),
    re_path(r'', include(api_patterns)),
    re_path(r'^$', views.FeeWaiverRoutingView.as_view(), name='home'),
    re_path(r'^contact/', views.FeeWaiverContactView.as_view(), name='ds_contact'),
    re_path(r'^admin_data/', views.FeeWaiverAdminDataView.as_view(), name='admin_data'),
    re_path(r'^further_info/', views.FeeWaiverFurtherInformationView.as_view(), name='ds_further_info'),
    re_path(r'^internal/', views.InternalView.as_view(), name='internal'),
    re_path(r'^external/', views.ExternalView.as_view(), name='external'),
    re_path(r'^account/$', views.ExternalView.as_view(), name='manage-account'),
    re_path(r'^profiles/', views.ExternalView.as_view(), name='manage-profiles'),
    re_path(r'^help/(?P<application_type>[^/]+)/(?P<help_type>[^/]+)/$', views.HelpView.as_view(), name='help'),
    re_path(r'^mgt-commands/$', views.ManagementCommandsView.as_view(), name='mgt-commands'),
    re_path(r'^internal/fee_waiver/(?P<feewaiver_pk>\d+)/$', views.InternalFeeWaiverView.as_view(), name='internal-feewaiver-detail'),
    re_path(r'^history/fee_waiver/(?P<pk>\d+)/$', views.FeeWaiverHistoryCompareView.as_view(), name='feewaiver_history'),
    path('private-media/<path:path>/', views.serve_private_file, name='serve_private_file'),
]  + ledger_patterns

if settings.DEBUG:  # Serve media locally in development.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.SHOW_DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns = [
        re_path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

