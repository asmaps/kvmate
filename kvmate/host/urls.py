from django.conf.urls import patterns
from django.conf.urls import url
from .views import HostListView, HostActionView, HostDetailView, HostEditView, HostCreateView

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
            regex=r'^(?P<name>[a-zA-Z0-9_\-]+)/$',
            view=HostDetailView.as_view(),
            name="info"
            ),
        url(
            regex=r'^edit/(?P<name>[a-zA-Z0-9_\-]+)/$',
            view=HostEditView.as_view(),
            name="edit"
            ),
        url(
            regex=r'^(?P<name>[a-zA-Z0-9_\-]+)/(?P<action>\w+)/$',
            view=HostActionView.as_view(),
            name="action"
            ),
        )
