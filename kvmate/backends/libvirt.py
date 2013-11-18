import libvirt
from celery.task import control as taskcontrol
# util
import logging
# errors
from libvirt import libvirtError
from django.core.exceptions import ObjectDoesNotExist

class LibvirtBackend():

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _get_domain(self, name):
        '''
        Return a domain object associated with the host
        '''
        try:
            domain = self.conn.lookupByName(name)
            return domain
        except libvirtError as e:
            print 'libvirt failed for host ' + name + ' with:'
            print str(e.get_error_code()) + ': ' + e.get_error_message()

    def _terminate_vnc(self, host):
        '''
        Terminates the VNC Websocket process attached to a Host object
        '''
        try:
            taskcontrol.revoke(host.vnc.id, terminate=True)
            host.vnc.delete()
            host.save()
        except ObjectDoesNotExist as e:
            self.logger.debug('tried terminating a nonexistant vnc process:')
            self.logger.debug(get_error_message())

    def set_name(self, host, old_name):
        pass

    def set_state(self, host):
        pass

    def set_vcpus(self, host):
        pass

    def set_memory(self, host):
        '''
        sets the amount of memory in kibibyte available for the specified host
        :returns: 1 if there is no change, 0 if done, -1 if there was an error
        '''
        domain = self._get_domain(host.name)
        if domain.maxMemory() == host.memory:
            self.logger.warning('unnesccessary set_memory for %s' % host.name)
            return 1
        else:
            try:
                domain.setMaxMemory(host.memory)
            except libvirt.libvirtError as e:
                self.logger.error('setting memory failed for %s with:' % host.name)
                self.logger.error(e.get_error_message())
                return -1
        self.logger.info('set_memory run for %s' % host.name)
        return 0

    def set_autostart(self, host):
        '''
        sets the autostart for the specified host
        :returns: 1 if there is no change, 0 if done, -1 if there was an error
        '''
        domain = self._get_domain(host.name)
        if domain.autostart() == host.autostart:
            self.logger.warning('unnesccessary set_autostart for %s' % host.name)
            return 1
        else:
            try:
                domain.setAutostart(host.autostart)
            except libvirt.libvirtError as e:
                self.logger.error('setting autostart failed for %s with:' % host.name)
                self.logger.error(e.get_error_message())
                return -1
        self.logger.info('set_autostart run for %s' % host.name)
        return 0

    def set_persistent(self, host):
        pass

    def start(self, host):
        '''
        Boots a domain
        :returns: 1 if the domain is already running, 0 if successful, -1 if there was an error
        '''
        domain = self._get_domain(host.name)
        if domain.isActive():
            self.logger.warning('unnesccessary start for %s' % host.name)
            return 1
        else:
            try:
                domain.create()
            except libvirt.libvirtError as e:
                self.logger.error('start failed for %s with:' % host.name)
                self.logger.error(e.get_error_message())
                return -1
        self.logger.info('start run for %s' % host.name)
        return 0 # all is fine

    def reboot(self, host):
        '''
        Reboots a domain
        :returns: 1 if the domain is not running, 0 if the reboot was successful, -1 if there was an error
        '''
        domain = self._get_domain(host.name)
        if not domain.isActive():
            self.logger.warning('unnesccessary reboot for %s' % host.name)
            return 1
        else:
            try:
                domain.reboot(0)
            except libvirt.libvirtError as e:
                self.logger.error('reboot failed for %s with:' % host.name)
                self.logger.error(e.get_error_message())
                return -1
            self._terminate_vnc(host)
        self.logger.info('reboot run for %s' % host.name)
        return 0 # all is fine

    def destroy(self, host):
        '''
        Destroys a domain matched by its hostname
        :returns: 1 if it was not running, 0 if the domain has been destroyed, -1 if there was an error
        '''
        domain = self._get_domain(host.name)
        if not domain.isActive():
            self.logger.warning('unnesccessary destroy for %s' % host.name)
            return 1
        else:
            try:
                domain.destroy()
            except libvirt.libvirtError as e:
                self.logger.error('destroy failed for %s with:' % host.name)
                self.logger.error(e.get_error_message())
                return -1
            self._terminate_vnc(host)
        self.logger.info('destroy run for %s' % host.name)
        return 0 # all is fine
