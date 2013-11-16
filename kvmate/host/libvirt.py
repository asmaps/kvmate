import libvirt
from libvirt import libvirtError
import xmltodict
from .models import Host
from .saltcalls import SaltCalls
from django.db import transaction
from celery.task import control as taskcontrol
from salt.wheel import key as saltkey
import salt

from kvmate.helpers import Helpers
from kvmate.saltcalls import SaltCalls

from django.conf import settings

class LibvirtHelpers:
    conn = None

    def __init__(self):
        conn = libvirt.open('qemu:///system')

    def _get_domain(self, host):
        '''
        Return a domain object associated with the hostname
        '''
        try:
            domain = self.conn.lookupByName(host.hostname)
            return domain
        except libvirtError as e:
            print 'libvirt failed for ' + host.hostname + ' with:'
            print str(e.get_error_code()) + ': ' + e.get_error_message()

    def adjust(self, host, fields):
        for field in fields:
            pass

    @transaction.commit_on_success
    def get_hosts(self):
        '''
        Update the DB with the vms
        '''
        # salt stuff
        s = SaltCalls()
        upgrades = s.get_upgrades_num()
        # discovery of hosts
        dead_hosts = [host.hostname for host in Host.objects.all()]
        domainlist = []
        for domain_id in self.conn.listDomainsID():
            domainlist.append(self.conn.lookupByID(domain_id))
        for name in self.conn.listDefinedDomains():
            domainlist.append(self.conn.lookupByName(name))
        for domain in domainlist:
            host, created = Host.objects.get_or_create(hostname=domain.name())
            if not created:
                dead_hosts.remove(host.hostname)
            if host.hostname in upgrades.keys():
                host.has_salt = True
                host.upgrades = upgrades[host.hostname]
            # data which will be enforced if somewhere but here
            host.is_on = True if domain.isActive() else False
            host.vcpus = domain.info()[3]
            host.ram = domain.info()[1]
            host.autostart = True if domain.autostart() else False
            host.persistent = True if domain.isPersistent() else False
            host.save()
        for hostname in dead_hosts:
            host = Host.objects.filter(hostname=hostname)[0]
            host.delete()

    def reboot(self, hostname):
        '''
        Reboots a domain matched by its hostname
        :returns: 1 if the domain is not running, 0 if the reboot was successful, -1 if there was an error
        '''
        # vm changes
        host = Host.objects.filter(hostname=hostname)[0]
        domain = self._get_domain(host)
        try:
            if domain.isActive():
                domain.reboot(0)
            else:
                return 1
        except libvirt.libvirtError as e:
            print 'reboot failed for ' + hostname + ' with:'
            print e.get_error_message()
            return -1
        # database changes
        try:
            taskcontrol.revoke(host.vnc.id)
            host.vnc.delete()
        except libvirt.libvirtError as e:
            print e.get_error_message()
        host.save()
        return 0

    def shutdown(self, hostname):
        '''
        Shutdown a domain matched by its hostname
        :returns: 1 if it was not running, 0 if the shutdown was successful, -1 if there was an error
        '''
        # vm changes
        host = Host.objects.filter(hostname=hostname)[0]
        domain = self._get_domain(host)
        try:
            if domain.isActive():
                domain.shutdown()
            else:
                return 1
        except libvirt.libvirtError as e:
            print 'shutdown failed for ' + hostname + ' with:'
            print e.get_error_message()
            return -1
        # database changes
        host.is_on = False
        try:
            taskcontrol.revoke(host.vnc.id)
            host.vnc.delte()
        except:
            pass
        host.save()
        return 0

    def destroy(self, hostname):
        '''
        Destroys a domain matched by its hostname
        :returns: 1 if it was not running, 0 if the domain has been destroyed, -1 if there was an error
        '''
        # vm changes
        host = Host.objects.filter(hostname=hostname)[0]
        domain = self._get_domain(host)
        try:
            if domain.isActive():
                domain.destroy()
            else:
                return 1
        except libvirt.libvirtError as e:
            print 'destroy failed for ' + hostname + ' with:'
            print e.get_error_message()
            return -1
        # database changes
        host.is_on = False
        try:
            taskcontrol.revoke(host.vnc.id)
            host.vnc.delte()
        except:
            pass
        host.save()
        return 0

    def set_autostart(self, hostname, state):
        '''
        sets the autostart for the specified host
        :returns: 1 if there is no change, 0 if done, -1 if there was an error
        '''
        # vm changes
        host = Host.objects.filter(hostname=hostname)[0]
        domain = self._get_domain(host)
        try:
            if domain.autostart() == state:
                return 1
            domain.setAutostart(state)
        except libvirt.libvirtError as e:
            print 'setting autostart failed for ' + hostname + ' with:'
            print e.get_error_message()
            return -1
        # database changes
        host.is_autostarted = state
        host.save()
        return 0

    def create(self, hostname):
        '''
        Creates a domain matched by its hostname
        :returns: 1 if the domain is already running, 0 if created, -1 if there was an error
        '''
        # vm changes
        host = Host.objects.filter(hostname=hostname)[0]
        domain = self._get_domain(host)
        try:
            if not domain.isActive():
                domain.create()
            else:
                return 1
        except libvirt.libvirtError as e:
            print 'start failed for ' + hostname + ' with:'
            print e.get_error_message()
            return -1
        # database changes
        host.is_on = True
        host.save()
        return 0

    def delete(self, hostname):
        '''
        Destroys and deletes a domain matched by its hostname
        :returns: 0 if the deletion was successful, -1 if there was an error
        '''
        # vm changes
        host = Host.objects.filter(hostname=hostname)[0]
        domain = self._get_domain(host)
        try:
            if domain.isActive():
                domain.destroy()
            domain.undefine()
            self.delete_storage_vol(hostname)
        except libvirt.libvirtError as e:
            print 'start failed for ' + hostname + ' with:'
            print e.get_error_message()
            return -1
        # database changes
        host.is_on = False
        if host.has_salt:
            saltkey.delete(hostname + '.*selfnet.de')
        try:
            taskcontrol.revoke(host.vnc.id)
            host.vnc.delte()
        except:
            pass
        host.save()
        return 0

    def vm_info(self, hostname):
        '''
        Build and return information based on libvirts xml definition
        '''
        host = Host.objects.filter(hostname=hostname)[0]
        domain = self._get_domain(host)
        raw = domain.info()
        doc = xmltodict.parse(domain.XMLDesc(0))
        nics = []
        rawnics = doc['domain']['devices']['interface']
        for rawnic in rawnics if type(rawnics) is list else [rawnics]:
            nic = {}
            nic['type'] = rawnic[u'@type']
            try:
                nic['model'] = rawnic[u'model'][u'@type']
            except:
                nic['model'] = ''
            nic['mac'] = rawnic[u'mac'][u'@address']
            nic['interface'] = rawnic[u'source'][u'@bridge']
            nics.append(nic)
        disks = []
        rawdisks = doc['domain']['devices']['disk']
        for rawdisk in rawdisks if type(rawdisks) is list else [rawdisks]:
            disk = {}
            if rawdisk['@device'] != u'disk':
                continue
            disk['type'] = rawdisk[u'@type']
            if disk['type'] == u'file':
                disk['source'] = rawdisk[u'source'][u'@file']
            elif disk['type'] == u'block':
                disk['source'] = rawdisk[u'source'][u'@dev']
            disks.append(disk)
        return {'cpu': int(raw[0]),
                'disks': disks,
                'nics': nics,
                'maxMem': int(raw[1]),
                'mem': int(raw[2])}


    def get_vnc(self, hostname):
        '''
        returns a dict with information on the virtual graphic adapter.
        '''
        host = Host.objects.filter(hostname=hostname)[0]
        out = {'autoport': 'None',
            'keymap': 'None',
            'remote_host': str(host.hyper),
            'listen': 'None',
            'port': 'None',
            'type': 'vnc'}
        domain = self._get_domain(host)
        doc = xmltodict.parse(domain.XMLDesc(0))
        try:
            out['autoport'] = str(doc['domain']['devices']['graphics']['@autoport'])
            out['listen'] = str(doc['domain']['devices']['graphics']['@listen'])
            out['port'] = str(doc['domain']['devices']['graphics']['@port'])
            out['type'] = str(doc['domain']['devices']['graphics']['@type'])
        except:
            print e.get_error_message()
        return out

    def make_vm(self, form_data, persistent):
        '''
        Creates a vm using the specified parameters
        :returns: 0 if successful, -1 if the hostname is already in use
        '''
        s = SaltCalls()
        s.update_kernel_stuff()
        kvm = 'yesguy' if form_data['kvm'] == 'kvm1' else 'wiseguy'
        host, created = Host.objects.get_or_create(hostname=form_data['hostname'])
        if created:
            h = Helpers()
            # define the domain
            self.conn.defineXML(h.gen_domain_xml(form_data))
            self.set_autostart(form['hostname'], True)
            self._create_storage_vol(form_data)
            h.gen_preseed(form_data)
            # enter the data into our db
            host.hyper = kvm
            host.has_salt = False # wait for a regular update with that
            host.is_autostarted = True
            host.is_persistent = persistent
            host.is_on = False
            host.save()
            # open the firewall for preseeding
            s = SaltCalls()
            s.open_firewall(form_data['ip'])
            # finally turn it on
            self.create(form_data['hostname'])
            return 0
        else:
            return -1

    def _create_storage_vol(self, form_data):
        hostname = form_data['hostname']
        kvm =  'yesguy' if form_data['kvm'] == 'kvm1' else 'wiseguy'
        conn = self.kvmconns[kvm]
        storage_pool = libvirt.virConnect.storagePoolLookupByName(conn,'lvm')
        h = Helpers()
        storage_vol_desc = h.gen_storage_vol_xml(form_data)
        libvirt.virStoragePool.createXML(storage_pool,storage_vol_desc,0)

    def delete_storage_vol(self, hostname):
    # TODO: actually delete it
        host = Host.objects.filter(hostname=hostname)[0]
        conn = self.kvmconns[host.hyper]
        storage_vol = libvirt.virConnect.storageVolLookupByPath(conn,'/dev/lvm/'+hostname)
        storage_vol.delete(0)
