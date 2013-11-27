# django message framework
from django.contrib import messages
# rendering of those messages using ajax and jquery
import json
from django.shortcuts import redirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.http import HttpResponse
# views and mixins
from django.views.generic import View, ListView, DetailView, CreateView
from django.views.generic.edit import ModelFormMixin
from braces.views import LoginRequiredMixin
# imports from within this app
from .models import Host
from .forms import HostForm
from .tasks import virtinstall

class HostListView(ListView):
    model = Host

    def get_queryset(self):
        queryset = super(HostListView, self).get_queryset()
        q = self.request.GET.get("q")
        if q:
            return queryset.filter(name__icontains=q)
        return queryset

class HostActionView(LoginRequiredMixin, View):
    def get(self, request, name, action):
        host = Host.objects.get(name=name)
        if action == 'start' or action == 'poweron':
            success = host.start()
            if success == 0:
                messages.add_message(request, messages.ERROR, 'Started the virtual machine "%s"' % name , 'success')
            elif success == 1:
                messages.add_message(request, messages.ERROR, 'The virtual machine "%s" is already running' % name , 'warning')
            elif success == -1:
                messages.add_message(request, messages.ERROR, 'Some error occured while starting the virtual machine "%s"' % name , 'danger')
        elif action == 'reboot' or action == 'restart':
            success = host.reboot()
            if success == 0:
                messages.add_message(request, messages.ERROR, 'Rebooted the virtual machine "%s"' % name , 'success')
            elif success == 1:
                messages.add_message(request, messages.ERROR, 'The virtual machine "%s" is not running' % name , 'warning')
            elif success == -1:
                messages.add_message(request, messages.ERROR, 'Some error occured while rebooting the virtual machine "%s"' % name , 'danger')
        elif action == 'halt' or action == 'shutdown' or action == 'poweroff':
            success = host.halt()
            if success == 0:
                messages.add_message(request, messages.ERROR, 'Shutdown the virtual machine "%s"' % name , 'success')
            elif success == 1:
                messages.add_message(request, messages.ERROR, 'The virtual machine "%s" is already shutdown' % name , 'warning')
            elif success == -1:
                messages.add_message(request, messages.ERROR, 'Some error occured while shutting down the virtual machine "%s"' % name , 'danger')
        elif action == 'kill' or action == 'forceoff':
            success = host.kill()
            if success == 0:
                messages.add_message(request, messages.ERROR, 'Forced the virtual machine "%s" off' % name , 'success')
            elif success == 1:
                messages.add_message(request, messages.ERROR, 'The virtual machine "%s" is already off' % namewarning, 'warning')
            elif success == -1:
                messages.add_message(request, messages.ERROR, 'Some error occured while forcing the virtual machine "%s" off' % namedanger, 'danger')
        if request.is_ajax():
            data = { 'msg': render_to_string('messages.html', {}, RequestContext(request)), }
            return HttpResponse(
                json.dumps(data, ensure_ascii=False),
                content_type="application/json" or "text/html"
            )
        else:
            return redirect('hosts')

class HostDetailView(DetailView):
    model = Host
    slug_field = 'name'
    slug_url_kwarg = 'name'

    def get_context_data(self, **kwargs):
        context = super(HostDetailView, self).get_context_data(**kwargs)
        context['memory_in_mb'] = context['object'].memory/1024
        return context

class HostCreateView(LoginRequiredMixin, CreateView):
    model = Host
    form_class = HostForm
    template_name_suffix = '_create_form'
    success_url = '/'
    initial = {'autostart': True, 'persistent': True, 'vcpus' : 1, 'memory' : 512 }

    def form_valid(self, form):
        self.object = form.save()
        self.object.memory = self.object.memory * 1024
        t = virtinstall.delay(form.data.copy())
        return super(ModelFormMixin, self).form_valid(form)
