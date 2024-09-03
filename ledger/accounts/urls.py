from django.urls import path, include
# from django.contrib.auth import views as auth_views

from ledger.accounts import views
from ledger.accounts.api import UserReportView, UserAccountsList, UserAccountsLogsList

app_name = 'accounts'

api_patterns = [
    path(r'api/report/duplicate_identity$', UserReportView.as_view(),name='ledger-user-report'),
    path(r'api/account/list$', UserAccountsList.as_view(),name='ledger-user-account'),
    path(r'api/account/logs/(?P<pk>\d+)$', UserAccountsLogsList.as_view(),name='ledger-user-account-logs'),
]

urlpatterns = [
    # url(r'^$', views.home, name='home'),
    path(r'^done/$', views.done, name='done'),
    path(r'^validation-sent/$', views.validation_sent, name='validation_sent'),
    path(r'^login-retry/$', views.login_retry, name='login_retry'),
    path(r'^login-expired/$', views.login_expired, name='login_expired'),
    path(r'^token-login/(?P<token>[^/]+)/(?P<email>[^/]+)/$', views.token_login, name='token_login'),
    path(r'^logout/', views.logout, name='logout'),
    path(r'^firsttime/', views.first_time, name='first_time'),
    path(r'accounts/', include(api_patterns)),
    path(r'account-management/(?P<pk>\d+)/change/$', views.AccountChange.as_view(), name='account_management_change'),    
    path(r'account-management/', views.AccountManagement.as_view(), name='account_management')
]
