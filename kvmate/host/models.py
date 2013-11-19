from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from backends.libvirt import LibvirtBackend

class Host(models.Model):
    name = models.CharField(max_length=64)
    is_on = models.BooleanField()
    # libvirt definitions (to be enforced on the hypervisor)
    vcpus = models.PositiveSmallIntegerField()
    memory = models.PositiveIntegerField()
    autostart = models.BooleanField()
    persistent = models.BooleanField()

    def start(self):
        self.is_on = True
        self.save(update_fields=['is_on'])

    def halt(self):
        self.is_on = False
        self.save(update_fields=['is_on'])

    def reboot(self):
        LibvirtBackend.reboot(self)

    def kill(self):
        self.is_on = False
        self.save()
        LibvirtBackend.destroy(self)

    def __unicode__(self):
        return 'KVMate.Host %s [On: %d]' % (self.hostname, self.is_on)

    def save(self, *args, **kwargs):
        '''
            if this hook should be used, save using host.save(update_fields = ['vcpu'])
        '''
        # intersect watched fields and update fields, save old values if needed
        triggered = [field for field in kwargs['update_fields'] if field in field_map.keys()]
        if 'name' in triggered:
            old_name = Host.objects.get(id=kwargs['instance'].id).name
        # perform the save to the database
        super(Host, self).save(*args, **kwargs)
        # enforce any changes made using the backends
        field_map = {
                'name' : LibvirtBackend.set_name,
                'is_on' : LibvirtBackend.set_state,
                'vcpus' : LibvirtBackend.set_vcpus,
                'memory' : LibvirtBackend.set_memory,
                'autostart' : LibvirtBackend.set_autostart,
                'persistent' : LibvirtBackend.set_persistent
                }
        for field in triggered:
            if field is 'name':
                field_map[field](kwargs['instance'], old_name)
            else:
                field_map[field](kwargs['instance'])
