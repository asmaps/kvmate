from django import forms
from .models import Host

class HostForm(forms.ModelForm):
    class Meta:
        model = Host
        fields = ('name', 'vcpus', 'memory', 'autostart', 'persistent',)

    def clean(self):
        cleaned_data = super(HostForm, self).clean()
        if cleaned_data.get('name') == None:
            self._errors['name'] = self.error_class(['Name may not be empty!'])
        if cleaned_data.get('vcpus') == None:
            self._errors['vcpus'] = self.error_class(['The number of virtual CPUs must not be empty!'])
        if cleaned_data.get('memory') == None:
            self._errors['memory'] = self.error_class(['The amount of memory must be specified!'])
        self.instance.is_on = True
        return cleaned_data
