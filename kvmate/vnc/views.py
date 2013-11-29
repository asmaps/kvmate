from django.shortcuts import redirect
from django.views.generic import View
from django.views.generic.base import TemplateView
from braces.views import LoginRequiredMixin
import json
from django.template import RequestContext
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.conf import settings
# django message framework
from django.contrib import messages

from host.models import Host
from .models import Vnc
from backends.mylibvirt import LibvirtBackend

class VncView(LoginRequiredMixin, TemplateView):
    template_name = 'vnc/vnc.html'

    def get(self, request, name):
        try:
            host = Host.objects.get(name=name)
        except Host.DoesNotExist:
            messages.add_message(self.request, messages.ERROR, 'The host "%s" is not in the database' % name, 'danger')
            return redirect('hosts')
        if host.is_on:
            return super(VncView, self).get(request, name)
        else:
            messages.add_message(self.request, messages.ERROR, 'This host is not running at the moment', 'warning')
            return redirect('hosts')

    def get_context_data(self, **kwargs):
        context = super(VncView, self).get_context_data(**kwargs)
        lvb = LibvirtBackend()
        host = Host.objects.get(name=self.kwargs['name'])
        success = lvb.attach_or_create_websock(self.request.user, host)
        context['name']=host.name
        if success == 0:
            context['host']=settings.VNC_HOST
            context['port']=host.vnc.port
        elif success == 1:
            messages.add_message(self.request, messages.ERROR, 'This host is not running at the moment', 'warning')
        elif success == -1:
            messages.add_message(self.request, messages.ERROR, 'An error occured retrieving the VNC parameters', 'danger')
        elif success == 2:
            messages.add_message(self.request, messages.ERROR, 'The host "%s" does not (yet) exist, but is in the database. This could mean that the host has been deleted without using kvmate, or that the host has not yet been created. If the latter is the case, allow a few seconds to start the boot process and reload this page' % self.kwargs['name'], 'danger')
        return context

class VncRestartView(LoginRequiredMixin, View):
    def get(self, request, name):
        try:
            Host.objects.get(name=name).vnc.delete()
            messages.add_message(self.request, messages.ERROR, 'The VNC session for the host "%s" has been reset for all users' % name, 'success')
        except Vnc.DoesNotExist:
            messages.add_message(self.request, messages.ERROR, 'VNC did not run for this host.', 'warning')
        return redirect('hosts')
