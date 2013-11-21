from django.conf.urls import patterns
from django.conf.urls import url
from .views import HostListView, HostActionView, HostDetailView, HostCreateView

urlpatterns = patterns("",
        url(
            regex=r'^$',
            view=HostListView.as_view(),
            name="hosts"
            ),
        url(
            regex=r'^create/$',
            view=HostCreateView.as_view(),
            name="create"
            ),
        url(
            regex=r'^(?P<name>\w+)/$',
            view=HostDetailView.as_view(),
            name="info"
            ),
        url(
            regex=r'^(?P<name>\w+)/(?P<action>\w+)/$',
            view=HostActionView.as_view(),
            name="action"
            ),
        )
