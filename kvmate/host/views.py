from django.shortcuts import render
from django.views.generic import ListView, CreateView
from .models import Host
from .forms import HostForm
from braces.views import LoginRequiredMixin

class HostList(ListView):
    model = Host

class CreateHost(LoginRequiredMixin, CreateView):
    model = Host
    form_class = HostForm
    template_name_suffix = '_create_form'
    success_url = '/'

    initial = {'autostart': True, 'persistent': True }

    def form_valid(self, form):
        return super(CreateHost, self).form_valid(form)
