from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'kvmate.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', RedirectView.as_view(url='/hosts', permanent=False), name='hosts'),
    url(r'^hosts/', include('host.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
