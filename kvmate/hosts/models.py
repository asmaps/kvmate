from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Host(models.Model):
    hostname = models.CharField(max_length=30, primary_key=True)
    is_on = models.BooleanField()
    # salt data (gathered)
    has_salt = models.BooleanField()
    upgrades_available = models.PositiveSmallIntegerField(default=1, blank=True, null=True)
    # libvirt definitions (to be enforced on the hypervisor)
    vcpus = models.PositiveSmallIntegerField()
    ram = models.PositiveIntegerField()
    diskspace = models.PositiveIntegerField()
    autostart = models.BooleanField()
    persistent = models.BooleanField()

    def start(self):
        pass

    def halt(self):
        pass

    def kill(self):
        pass

    def __unicode__(self):
        return 'KVMate.Host %s [On: %d]' % (self.hostname, self.is_on)

# if the following hooks should be used, save using vhost.save(update_fields['vcpu'])
@receiver(post_save, sender = Host)
def adjust_host(sender, **kwargs):
    trigger_fields = ['vcpus', 'ram', 'diskspace', 'autostart', 'persistent']
    updates = [trigger for trigger in kwargs['update_fields'] if trigger in trigger_fields]
    backend.adjust(kwargs['instance'], updates)
