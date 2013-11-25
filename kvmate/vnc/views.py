from django.shortcuts import render
from django.views.generic.base import TemplateView
from braces.views import LoginRequiredMixin

from host.models import Host
from backends.mylibvirt import LibvirtBackend

class VncView(LoginRequiredMixin, TemplateView):
    template_name = 'vnc/vnc.html'

    def get_context_data(self, **kwargs):
        context = super(VncView, self).get_context_data(**kwargs)
        lvb = LibvirtBackend()
        host = Host.objects.get(name=kwargs['name'])
        success = lvb.attach_or_create_websock(self.request.user, host)
        if success == 0:
            context['host']='10.4.114.97'
            context['port']=host.vnc.port
            return context
        else:
            print success
            print 'fuck this'
