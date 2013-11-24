from django.db import models
from host.models import Host

class VNC(models.Model):
    host = models.OneToOneField(Host,primary_key=True)
    port = models.IntegerField()
    def __unicode__(self):
        return 'KVMate.VNC [Port: %d]' % self.port
