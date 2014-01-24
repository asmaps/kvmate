from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView
from django.contrib.auth.views import login, logout

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(
        regex=r'^login/$',
        view=login,
        kwargs={'template_name': 'kvmate/login.html'},
        name='login'
    ),
    url(
        regex=r'^logout/$',
        view=logout,
        kwargs={'template_name': 'kvmate/logout.html'},
        name='logout'
    ),
    url(
        regex=r'^$',
        view=RedirectView.as_view(url='/hosts', permanent=False)
    ),

    url(r'^hosts/', include('host.urls', namespace='host')),
    url(r'^vnc/', include('vnc.urls')),
    url(r'^admin/', include(admin.site.urls)),
) + staticfiles_urlpatterns()
