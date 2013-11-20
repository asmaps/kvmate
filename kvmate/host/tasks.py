import libvirt
import logging

from celery.task.schedules import crontab
from celery.decorators import periodic_task
from django.db import transaction

from .models import Host

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
        host, created = Host.objects.get_or_create(
                name=domain.name(),
                is_on = True if domain.isActive() else False,
                vcpus = domain.info()[3],
                memory = domain.info()[1],
                autostart = True if domain.autostart() else False,
                persistent = True if domain.isPersistent() else False
                )
        if created:
            logger.info('new host %s found, adding to database' % host.name)
        else:
            logger.info('host %s found, updating' % host.name)
            dead_hosts.remove(host.name)
        host.save()
    # delete vanished hosts from our database
    for hostname in dead_hosts:
        logger.warning('host %s has been deleted outside kvmate, removing' % hostname)
        host = Host.objects.filter(hostname=hostname)[0]
        host.delete()
    conn.close()
