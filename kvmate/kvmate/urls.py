from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView
from django.contrib.auth.views import login, logout

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'kvmate.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^login/$', login, {'template_name': 'kvmate/login.html'}, name='login'),
    url(r'^logout/$', logout, {'template_name': 'kvmate/logout.html'}, name='logout'),

    url(r'^$', RedirectView.as_view(url='/hosts', permanent=False)),
    url(r'^hosts/', include('host.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
