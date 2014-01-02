import logging
import libvirt
from xml.dom.minidom import parseString
from celery.result import AsyncResult
from django.core.exceptions import ObjectDoesNotExist
from vnc.models import Vnc
from .tasks import start_websock

class LibvirtBackend():

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.conn = libvirt.open('qemu:///system')

    def _get_domain(self, name):
        '''
        Return a domain object associated with the host
        '''
        try:
            domain = self.conn.lookupByName(name)
            return domain
        except libvirt.libvirtError as e:
            print 'libvirt failed for host ' + name + ' with:'
            print str(e.get_error_code()) + ': ' + e.get_error_message()

    def terminate_vnc(self, host):
        '''
        Terminates the VNC Websocket process attached to a Host object
        '''
        try:
            host.vnc.delete()
            host.save()
        except ObjectDoesNotExist as e:
            self.logger.info('tried deleting a nonexistant vnc database entry')

    def set_name(self, host, old_name):
        #TODO make critical error less critical
        '''
        renames a libvirt domain by redefining it
        :returns: 1 if no change was required, 0 if successful, -1 if there was an error
        '''
        if old_name == host.name:
            self.logger.warning('unnesccessary set_name for %s' % host.name)
            return 1
        old_domain = self._get_domain(old_name)
        if old_domain.isActive():
            self.logger.error('cannot change the name of a running domain')
            host.name = old_name
            host.save()
            return -1
        else:
            try:
                #xml = xmltodict.parse(domain.XMLDesc(0))
                old_domain.undefine()
                xml.replace('<name>' + old_name + '</name>', '<name>' + host.name + '</name>')
                libvirt.defineXML(xml)
            except libvirt.libvirtError as e:
                self.logger.critical('set_name %s (old: %s) failed' % (host.name, old_name))
                self.logger.critical("check the domain definition's integrity on the hypervisor")
                self.logger.critical(e.get_error_message())
                return -1
        return 0 # all is fine

    def set_state(self, host):
        '''
        Adapt a domains status to the is_on value in the database
        :returns: 1 if no change was required, 0 if successful, -1 if there was an error
        '''
        domain = self._get_domain(host.name)
        if host.is_on and not domain.isActive():
            return self.start(host)
        elif not host.is_on and domain.isActive():
            return self.shutdown(host)
        else:
            self.logger.warning('unnesccessary set_state for %s' % host.name)
            return 1

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
        return 0 # all is fine

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
        return 0 # all is fine

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
            self.terminate_vnc(host)
        self.logger.info('reboot run for %s' % host.name)
        return 0 # all is fine

    def shutdown(self, host):
        '''
        shuts a domain down
        :returns: 1 if the domain is already stopped, 0 if successful, -1 if there was an error
        '''
        domain = self._get_domain(host.name)
        if not domain.isActive():
            self.logger.warning('unnesccessary shutdown for %s' % host.name)
            return 1
        else:
            try:
                domain.shutdown()
            except libvirt.libvirtError as e:
                self.logger.error('shutdown failed for %s with:' % host.name)
                self.logger.error(e.get_error_message())
                return -1
        self.logger.info('shutdown run for %s' % host.name)
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
            self.terminate_vnc(host)
        self.logger.info('destroy run for %s' % host.name)
        return 0 # all is fine

    def attach_or_create_websock(self, user, host):
        '''
        Creates a websocket for the specified host
        :returns: 1 if the host is not running, 0 and the port if the websocket is running, -1 if
        there is no VNC support for this domain
        '''
        domain = self._get_domain(host.name)
        if domain is None:
            self.logger.warning('vnc requested for the host %s, which does not exist in libvirt (yet)' % host.name)
            return 2
        elif not domain.isActive():
            self.logger.warning('vnc requested for the shutdown host %s' % host.name)
            return 1
        else:
            if hasattr(host, 'vnc'):
                if not AsyncResult(host.vnc.pid).ready():
                    self.logger.info('session of %s is blocked for %s by another user' % (host.name, user))
                    return -2
                else:
                    host.vnc.delete()
            self.logger.info('initializing vnc for %s' % host.name)
            doc = parseString(domain.XMLDesc(0))
            domain_node = doc.getElementsByTagName('domain')[0]
            graphics_node = domain_node.getElementsByTagName('graphics')[0]
            if graphics_node is None or graphics_node.getAttribute('type') != u'vnc':
                # vm does not support vnc
                return -1
            target_port = graphics_node.getAttribute('port')
            port = int(graphics_node.getAttribute('port'))+10000
            t = start_websock.delay(str(target_port), str(port))
            vnc = Vnc(host=host,port=port, pid=t.id)
            vnc.save()
            self.logger.info('websocket started for %s on port %d' % (host.name, host.vnc.port))
            host.vnc = vnc
            host.save()
            return 0 # all is fine
