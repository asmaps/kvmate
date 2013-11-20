from django.conf.urls import patterns
from django.conf.urls import url
from .views import HostList, CreateHost

urlpatterns = patterns("",
        url(
            regex=r'^$',
            view=HostList.as_view(),
            name="hosts"
            ),
        url(
            regex=r'^create/$',
            view=CreateHost.as_view(),
            name="create"
            ),
        )
