import logging
from django.db import models

from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from celery.task.control import revoke

class Vnc(models.Model):
    host = models.OneToOneField('host.Host')
    pid  = models.CharField(max_length=100)
    port = models.IntegerField()
    users = models.ManyToManyField(User)
    def __unicode__(self):
        return 'KVMate.VNC with PID %s [Port: %d]' % (self.pid, self.port)

@receiver(user_logged_out)
def on_logout(sender, **kwargs):
    user = kwargs['user']
    if user is None:
        return
    logger = logging.getLogger(__name__)
    logger.info('user %s logged out' % user.username)
    for conn in Vnc.objects.all():
        if user in conn.users.all():
            logger.info('removing user %s from %s vnc' % (user.username, conn.host.name))
            conn.users.remove(user)
            if conn.users.count() == 0:
                logger.info('VNC session for host %s unused, killing' % conn.host.name)
                revoke(conn.pid, terminate=True)
                conn.delete()
