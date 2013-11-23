from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponse
from django.views.generic import View, ListView, DetailView, CreateView
from django.views.generic.edit import ModelFormMixin
from .models import Host
from .forms import HostForm
from braces.views import LoginRequiredMixin

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
            host.start()
        elif action == 'reboot' or action == 'restart':
            messages.add_message(request, messages.ERROR, 'restarted', 'success')
            host.reboot()
        elif action == 'halt' or action == 'shutdown' or action == 'poweroff':
            host.halt()
        elif action == 'kill' or action == 'forceoff':
            host.kill()
        if request.is_ajax():
            return HttpResponse(200)
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
    initial = {'autostart': True, 'persistent': True, 'vcpus' : 1, 'memory' : 524288 }

    def form_valid(self, form):
        self.object = form.save()
        return super(ModelFormMixin, self).form_valid(form)
