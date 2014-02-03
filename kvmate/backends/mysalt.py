import logging
from salt import client, runner, wheel

from django.conf import settings

from kvmate.models import Host

class SaltBackend(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = client.LocalClient()
        self.runner = runner.RunnerClient()
        self.wheel = wheel.WheelClient()

    def _terminate_vnc(self, host):
        '''
        Terminates the VNC Websocket process attached to a Host object
        '''
        try:
            host.vnc.delete()
            host.save()
        except ObjectDoesNotExist as e:
            self.logger.info('tried deleting a nonexistant vnc database entry')

    def set_name(self, host, old_name):
        """
        Just say 'did it!'
        """
        self.logger.debug('MySalt\'s set_name was called with host=%s and old_name=%s' % (host, old_name))
        return 0  # all is fine

    def set_state(self, host):
        """
        Just say 'did it!'
        """
        self.logger.debug('MySalt\'s set_state was called with host=%s' % host)
        return 0  # all is fine

    def set_vcpus(self, host):
        """
        Just say 'did it!'
        """
        self.logger.debug('MySalt\'s set_vcpus was called with host=%s' % host)
        return 0  # all is fine

    def set_memory(self, host):
        """
        Just say 'did it!'
        """
        self.logger.debug('MySalt\'s set_memory was called with host=%s' % host)
        return 0  # all is fine

    def set_autostart(self, host):
        """
        Just say 'did it!'
        """
        self.logger.debug('MySalt\'s set_autostart was called with host=%s' % host)
        return 0  # all is fine

    def set_persistent(self, host):
        """
        Just say 'did it!'
        """
        self.logger.debug('MySalt\'s set_persistent was called with host=%s' % host)
        return 0  # all is fine

    def start(self, host):
        """
        Just say 'did it!'
        """
        self.logger.debug('MySalt\'s start was called with host=%s' % host)
        return 0  # all is fine

    def reboot(self, host):
        """
        Just say 'did it!'
        """
        self.logger.debug('MySalt\'s reboot was called with host=%s' % host)
        return 0  # all is fine

    def shutdown(self, host):
        """
        Just say 'did it!'
        """
        self.logger.debug('MySalt\'s shutdown was called with host=%s' % host)
        return 0  # all is fine

    def destroy(self, host):
        """
        Just say 'did it!'
        """
        self.logger.debug('MySalt\'s destroy was called with host=%s' % host)
        return 0  # all is fine

    def attach_or_create_websock(self, user, host):
        """
        Return no support for domain
        """
        self.logger.debug('MySalt\'s attach_or_create_websock was called with user=%s and host=%s' % (user, host))
        return -1  # no support
