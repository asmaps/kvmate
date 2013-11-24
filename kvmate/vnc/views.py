from django.shortcuts import render
from django.views.generic.base import TemplateView
from braces.views import LoginRequiredMixin

from .models import Host
from backends.mylibvirt import LibvirtBackend

class VncView(LoginRequiredMixin, TemplateView):
    def get(self, request, name):
        lvb = LibvirtBackend()
        host = Host.objects.get(name=name)
        success, port = lvb.create_websock(host)
