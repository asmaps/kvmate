import logging

from django.db import models
from django.contrib.auth.models import User

from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.contrib.auth.signals import user_logged_out

from os import kill
from signal import SIGTERM

class Vnc(models.Model):
    host = models.OneToOneField('host.Host')
    pid  = models.PositiveIntegerField()
    port = models.PositiveIntegerField()
    users = models.ManyToManyField(User, null=True, blank=True)
    def __unicode__(self):
        return 'KVMate.VNC with PID %s [Port: %d]' % (self.pid, self.port)

@receiver(pre_delete, sender=Vnc)
def on_delete(sender, instance, **kwargs):
    # TODO: maybe make this an overwrite of the delete() function?
    logger = logging.getLogger(__name__)
    logger.info('Vnc session of host %s deleted, killing websocket' % instance.host.name)
    try:
        kill(int(instance.pid), SIGTERM)
    except OSError:
        logger.info('Websocket for %s was already dead' % instance.host.name)

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
                logger.info('VNC session for host %s unused, deleting' % conn.host.name)
                conn.delete()
