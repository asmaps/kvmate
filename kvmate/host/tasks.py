import libvirt

from django.db import transaction
from celery.task.schedules import crontab
from celery.decorators import periodic_task

from .models import Host

@periodic_task(run_every=crontab(hour="*", minute="*/10", day_of_week="*"))
@transaction.commit_on_success
def update_hosts():
    '''
    Update the database
    '''
    conn = libvirt.open('qemu:///system')
    dead_hosts = [host.hostname for host in Host.objects.all()]
    domainlist = []
    # get running VMs
    for domain_id in conn.listDomainsID():
        domainlist.append(conn.lookupByID(domain_id))
    # get defined, but shutdown VMs
    for name in conn.listDefinedDomains():
        domainlist.append(conn.lookupByName(name))
    # mirror or confirm them in our database
    for domain in domainlist:
        host, created = Host.objects.get_or_create(name=domain.name())
        if not created:
            dead_hosts.remove(host.name)
        host.is_on = True if domain.isActive() else False
        host.vcpus = domain.info()[3]
        host.memory = domain.info()[1]
        host.autostart = True if domain.autostart() else False
        host.persistent = True if domain.isPersistent() else False
        host.save()
    # delete vanished hosts from our database
    for hostname in dead_hosts:
        host = Host.objects.filter(hostname=hostname)[0]
        host.delete()
    conn.close()
