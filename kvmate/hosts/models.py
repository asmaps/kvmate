from django.db import models

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

    def set_mem(self):
        pass

    def set_vcpus(self):
        pass

    def set_disk(self):
        pass

    def __unicode__(self):
        return 'KVMate.Host %s [On: %d]' % (self.hostname, self.is_on)

# if the following hooks should be used, save using vhost.save(update_fields['vcpu'])
# TODO: test if update_fields is a logical OR or an exact match
@receiver(post_save, sender = Host, update_fields = ['vcpus'])
def adjust_vcpus(sender, **kwargs):
    backend.set_vcpu(kwargs['instance'])

@receiver(post_save, sender = Host, update_fields = ['ram'])
def adjust_ram(sender, **kwargs):
    backend.set_ram(kwargs['instance'].ram)

@receiver(post_save, sender = Host, update_fields = ['diskspace'])
def adjust_diskspace(sender, **kwargs):
    backend.set_diskspace(kwargs['instance'].diskspace)

@receiver(post_save, sender = Host, update_fields = ['autostart'])
def adjust_autostart(sender, **kwargs):
    backend.set_autostart(kwargs['instance'].autostart)

@receiver(post_save, sender = Host, update_fields = ['persistent'])
def adjust_persistent(sender, **kwargs):
    backend.set_persistent(kwargs['instance'].persistent)
