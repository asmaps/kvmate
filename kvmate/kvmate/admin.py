from django.contrib import admin
from host.models import Host
from vnc.models import VNC

admin.site.register(Host)
admin.site.register(VNC)
