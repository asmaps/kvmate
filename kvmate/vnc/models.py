from django.db import models

class Vnc(models.Model):
    host = models.OneToOneField('host.Host')
    pid  = models.CharField(max_length=100)
    port = models.IntegerField()
    def __unicode__(self):
        return 'KVMate.VNC with PID %s [Port: %d]' % (self.pid, self.port)
