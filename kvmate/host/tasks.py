import libvirt
import logging

from celery import task
import shlex
from subprocess import call
from django.template.loader import render_to_string

from celery.task.schedules import crontab
from celery.decorators import periodic_task
from django.db import transaction
from django.conf import settings

from .models import Host

@task
def virtinstall(data):
    def render_to_file(template, filename, data):
        open(filename, "w").write(render_to_string(template, data))
    logger = logging.getLogger(__name__)
    # TODO: get the following from settings
    # virtinstall settings
    data['netinstall'] = "http://mirror.selfnet.de/debian/dists/wheezy/main/installer-amd64/"
    data['bridge'] = "br0"
    data['poolname'] = "virtimages"
    data['disksize'] = "5"
    if data['autostart']:
        data['autostartflag'] = "--autostart "
    data['preseedpath'] = "/home/danieln/kvmate/kvmate/host/static/host/preseed-" + data['name'] + ".cfg"
    data['preseedurl'] = "172.16.0.10:8000/static/host/preseed-" + data['name'] + ".cfg"
    # preseed settings
    data['mirror'] = "mirror.selfnet.de"
    data['timezone'] = "Europe/Berlin"
    data['ntpserver'] = "ntp.selfnet.de"
    data['initial_password'] = "geheim42"
    # make preseedfile
    render_to_file("host/preseed.cfg", data['preseedpath'], data)
    # make and run virtinstall command
    command = render_to_string("host/virtinstall.sh", data)
    logger.info('running virtinstall with: ' + command)
    call(shlex.split(command))

@periodic_task(run_every=crontab(hour="*", minute="*/10", day_of_week="*"))
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
