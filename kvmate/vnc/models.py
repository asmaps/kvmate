import logging
from django.db import models

from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from celery.task.control import revoke
from host.models import Host

class VNC(models.Model):
    host = models.OneToOneField(Host,primary_key=True)
    pid  = models.CharField(max_length=100)
    port = models.IntegerField()
    users = models.ManyToManyField(User)
    def __unicode__(self):
        return 'KVMate.VNC mit ID %s [Port: %d]' % (self.vnc_id, self.vn_port)

@receiver(user_logged_out)
def on_logout(sender, **kwargs):
    logger = logging.getLogger(__name__)
    user = kwargs['user']
    logger.info('user %s logged out' % user.username)
    for conn in VNC.objects.all():
        if user in conn.users.all():
            logger.debug('removing user %s from %s vnc' % (user.username, conn.host.hostname))
            conn.users.remove(user)
            if conn.users.count() == 0:
                logger.debug('VNC session for host %s unused, killing' % conn.host.hostname)
                revoke(conn.id, terminate=True)
                conn.delete()
