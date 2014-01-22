import libvirt
import logging

from celery import shared_task
import shlex
from subprocess import call
from django.template.loader import render_to_string

from celery.task.schedules import crontab
from celery.decorators import periodic_task
from django.db import transaction
from django.conf import settings

from .models import Host

@shared_task
def virtinstall(data):
    def render_to_file(template, filename, data):
        open(filename, "w").write(render_to_string(template, data))
    logger = logging.getLogger(__name__)
    logger.info('creating new host')
    # virtinstall settings
    data['netinstall'] = settings.NETINSTALL_URL
    data['bridge'] = settings.BRIDGE_TYPE + ':' + settings.BRIDGE_NAME
    data['poolname'] = settings.STORAGEPOOL_NAME
    data['disksize'] = settings.DISKSIZE
    if data['autostart']:
        data['autostartflag'] = "--autostart "
    if data['iptype'] == 'static':
        data['virtinstnetwork'] = 'netcfg/get_ipaddress=' + data['ip'] + ' netcfg/get_netmask=' + data['netmask'] + ' netcfg/get_gateway=' + data['gateway'] + ' netcfg/get_nameservers=' + data['dns'] + ' netcfg/disable_dhcp=true'
    elif data['iptype'] == 'dynamic':
        data['virtinstnetwork'] = 'netcfg/disable_dhcp=false'
    data['preseedpath'] = settings.PRESEEDPATH + "preseed-" + data['name'] + ".cfg"
    data['preseedurl'] = settings.PRESEED_HOST + ":" + settings.PRESEED_PORT + settings.STATIC_URL + "host/preseed-" + data['name'] + ".cfg"
    # preseed settings
    if data['iptype'] == 'static':
        data['preseednetwork'] = 'd-i netcfg/get_nameservers string ' + data['dns'] + '\nd-i netcfg/get_ipaddress string ' + data['ip'] + '\nd-i netcfg/get_netmask string ' + data['netmask'] + '\nd-i netcfg/get_gateway string ' + data['gateway'] + '\nd-i netcfg/confirm_static boolean true'
    elif data['iptype'] == 'dynamic':
        data['preseednetwork'] = 'd-i netcfg/disable_dhcp boolean false'
    data['mirror'] = settings.DEFAULT_MIRROR
    data['timezone'] = settings.DEFAULT_TIMEZONE
    data['ntpserver'] = settings.DEFAULT_NTPSERVER
    data['initial_password'] = settings.INITIAL_PASSWORD
    # make preseedfile
    render_to_file("host/preseed.cfg", data['preseedpath'], data)
    # make and run virtinstall command
    command = render_to_string("host/virtinstall.sh", data)
    logger.info('running virtinstall with: ' + command)
    #FIXME: make configurable via settings
    import os
    os.environ['HOME'] = '/home/kvmate/' # override ~ for ~/.virtinst
    call(shlex.split(command))

@shared_task
def update_hosts():
    '''
    Update the database
    '''
    logger = logging.getLogger(__name__)
    conn = libvirt.open('qemu:///system')
    dead_hosts = [host.name for host in Host.objects.all()]
    domainlist = []
    # get running VMs
    logger.info('retrieving hosts from libvirt')
    for domain_id in conn.listDomainsID():
        domainlist.append(conn.lookupByID(domain_id))
    # get defined, but shutdown VMs
    for name in conn.listDefinedDomains():
        domainlist.append(conn.lookupByName(name))
    # mirror or confirm them in our database
    for domain in domainlist:
        try:
            host = Host.objects.get(name=domain.name())
            logger.info('host %s found, checking for changes...' % host.name)
            new_data = {}
            new_data['is_on'] = True if domain.isActive() else False
            new_data['vcpus'] = domain.info()[3]
            new_data['memory'] = domain.info()[1]
            new_data['autostart'] = True if domain.autostart() else False
            new_data['persistent'] = True if domain.isPersistent() else False
            if new_data['is_on'] != host.is_on:
                logger.info('host %s updated is_on: %s -> %s' % (host.name, host.is_on, new_data['is_on']))
                # if the host was on, try to kill possible websocket processes
                if host.is_on:
                    logger.info('try to kill a possible stray vnc process of host %s' % host.name)
                    lvb = backends.mylibvirt.LibvirtBackend()
                    lvb.terminate_vnc(host)
                host.is_on = new_data['is_on']
            if new_data['vcpus'] != host.vcpus:
                logger.info('host %s updated vcpus: %s -> %s' % (host.name, host.vcpus, new_data['vcpus']))
                host.vcpus = new_data['vcpus']
            if new_data['memory'] != host.memory:
                logger.info('host %s updated memory: %s -> %s' % (host.name, host.memory, new_data['memory']))
                host.memory = domain.info()[1]
            if new_data['autostart'] != host.autostart:
                logger.info('host %s updated autostart: %s -> %s' % (host.name, host.autostart, new_data['autostart']))
                host.autostart = new_data['autostart']
            if new_data['persistent'] != host.persistent:
                logger.info('host %s updated persistent: %s -> %s' % (host.name, host.persistent, new_data['persistent']))
                host.persistent = new_data['persistent']
            host.save()
            dead_hosts.remove(host.name)
        except Host.DoesNotExist:
            logger.info('new host %s found, adding to database' % domain.name())
            host = Host.objects.create(
                name=domain.name(),
                is_on = True if domain.isActive() else False,
                vcpus = domain.info()[3],
                memory = domain.info()[1],
                autostart = True if domain.autostart() else False,
                persistent = True if domain.isPersistent() else False
                )
    # delete vanished hosts from our database
    for name in dead_hosts:
        logger.warning('host %s has been deleted outside kvmate, removing' % name)
        host = Host.objects.filter(name=name)[0]
        host.delete()
    conn.close()
    logger.info('retrieved and updated all hosts from libvirt')
