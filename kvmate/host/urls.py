from django.conf.urls import patterns
from django.conf.urls import url
from .views import (
    HostOverviewView, HostActionView, HostDetailView, HostUpdateView, HostCreateView, AjaxHostOverviewTableView)

urlpatterns = patterns(
    "",
    url(r'^$', HostOverviewView.as_view(), name="overview"),
    url(r'^create/$', HostCreateView.as_view(), name="create"),
    url(r'^(?P<name>[a-zA-Z0-9_\-]+)/$', HostDetailView.as_view(), name="info"),
    url(r'^edit/(?P<name>[a-zA-Z0-9_\-]+)/$', HostUpdateView.as_view(), name="update"),
    url(r'^(?P<name>[a-zA-Z0-9_\-]+)/(?P<action>(%s))/$' % '|'.join(HostActionView.allowed_actions),
        HostActionView.as_view(), name="action"),

    #ajax
    url(r'^ajax/overview_table/$', AjaxHostOverviewTableView.as_view(), name="overview_table_ajax"),
)