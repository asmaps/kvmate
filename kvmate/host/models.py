from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from backends.mylibvirt import LibvirtBackend

class Host(models.Model):
    name = models.SlugField(unique=True, max_length=64)
    is_on = models.BooleanField()
    # libvirt definitions (to be enforced on the hypervisor)
    vcpus = models.PositiveSmallIntegerField(verbose_name="Number of virtual CPUs")
    memory = models.PositiveIntegerField(verbose_name="Maximum amount of memory")
    autostart = models.BooleanField(verbose_name="Autostart this host")
    persistent = models.BooleanField(verbose_name="Make persistent")

    lvb = LibvirtBackend()
    field_map = {
            'name' : lvb.set_name,
            'is_on' : lvb.set_state,
            'vcpus' : lvb.set_vcpus,
            'memory' : lvb.set_memory,
            'autostart' : lvb.set_autostart,
            'persistent' : lvb.set_persistent
            }

    def start(self):
        self.is_on = True
        self.save()
        return self.lvb.start(self)

    def halt(self):
        self.is_on = False
        self.save()
        return self.lvb.shutdown(self)

    def reboot(self):
        self.lvb.reboot(self)
        return self.lvb.reboot(self)

    def kill(self):
        self.is_on = False
        self.save()
        return self.lvb.destroy(self)

    def __unicode__(self):
        return 'KVMate.Host %s [On: %d]' % (self.name, self.is_on)

    def save(self, *args, **kwargs):
        '''
            if this hook should be used, save using host.save(update_fields = ['vcpu'])
        '''
        try:
            # intersect watched fields and update fields, save old values if needed
            triggered = [field for field in kwargs['update_fields'] if field in self.field_map.keys()]
            if 'name' in triggered:
                old_name = Host.objects.get(id=self.id).name
            # enforce any changes made using the backends
            for field in triggered:
                if field is 'name':
                    self.field_map[field](self, old_name)
                else:
                    self.field_map[field](self)
        except KeyError:
            pass
        finally:
            # perform the save to the database
            super(Host, self).save(*args, **kwargs)
