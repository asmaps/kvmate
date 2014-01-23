from django import forms
from django.conf import settings

from .models import Host

class HostForm(forms.ModelForm):
    disksize = forms.IntegerField()
    iptype = forms.ChoiceField((('static', 'Static'), ('dynamic', 'Dynamic (using DHCP)'), ), label='Networking')
    ip = forms.GenericIPAddressField(label='IP', initial=settings.CREATE_HOST_DEFAULT_IP, required=False)
    netmask = forms.GenericIPAddressField(required=False, initial=settings.CREATE_HOST_DEFAULT_NETMASK)
    gateway = forms.GenericIPAddressField(required=False, initial=settings.CREATE_HOST_DEFAULT_GATEWAY)
    dns = forms.GenericIPAddressField(label='DNS Server', required=False, initial=settings.CREATE_HOST_DEFAULT_DNS)
    domain = forms.CharField(label='Domain Name', required=False, initial=settings.CREATE_HOST_DEFAULT_DOMAIN)
    setup_script_url = forms.URLField(help_text='URL to a shell script that will be executed after installation',
                                      initial=settings.CREATE_HOST_DEFAULT_SETUP_SCRIPT)

    class Meta:
        model = Host
        fields = ('name', 'vcpus', 'memory', 'disksize', 'autostart', 'persistent', 'iptype',)

    def clean(self):
        cleaned_data = super(HostForm, self).clean()
        if cleaned_data.get('name') == None:
            self._errors['name'] = self.error_class(['Name may not be empty!'])
        if cleaned_data.get('vcpus') == None:
            self._errors['vcpus'] = self.error_class(['The number of virtual CPUs must not be empty!'])
        if cleaned_data.get('memory') == None:
            self._errors['memory'] = self.error_class(['The amount of memory must be specified!'])
        if cleaned_data.get('iptype') == 'static':
            if cleaned_data.get('ip') == '':
                self._errors['ip'] = self.error_class(['The IP must be specified if static is selected!'])
            if cleaned_data.get('netmask') == '':
                self._errors['netmask'] = self.error_class(['The netmask must be specified if static is selected!'])
            if cleaned_data.get('gateway') == '':
                self._errors['gateway'] = self.error_class(['The gateway must be specified if static is selected!'])
            if cleaned_data.get('dns') == '':
                self._errors['dns'] = self.error_class(['The DNS Server must be specified if static is selected!'])
        self.instance.is_on = True
        return cleaned_data
