from django.conf.urls import patterns
from django.conf.urls import url
from .views import HostList

urlpatterns = patterns("",
        url(
            regex=r'^$',
            view=HostList.as_view(),
            name="HostList"
            ),
        )
