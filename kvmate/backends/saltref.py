import salt.client
from kvmate.models import Host

from django.conf import settings

class SaltCalls:

    def get_upgrades_num(self):
        client = salt.client.LocalClient()
        raw = client.cmd('*', 'pkg.list_upgrades', ['refresh=False'])
        data = {host.split('.')[0]: len(packages.keys()) for (host, packages) in raw.iteritems()}
        return data


    def highstate(self, hostname):
        client = salt.client.LocalClient()
        client.cmd_async(hostname + '*', 'state.highstate', ret='smtp_return')


    def host_info(self, hostname):
        host = Host.objects.filter(hostname=hostname)[0]
        if host.has_salt:
            fqdn = hostname + '*'
            client = salt.client.LocalClient()
            ret = client.cmd(fqdn, 'status.all_status')
            data = {}
            data['uptime'] = ret[ret.keys()[0]]['uptime']
            data['memTotal'] = float(ret[ret.keys()[0]]['meminfo']['MemTotal']['value']) / 1024.0 # TODO: honor the unit provided by salt
            data['memUsed'] = (float(ret[ret.keys()[0]]['meminfo']['MemTotal']['value']) - float(ret[ret.keys()[0]]['meminfo']['MemFree']['value'])) / 1024.0
            data['memPercent'] = int(( data['memUsed'] * 100 ) / data['memTotal'])
            ret = client.cmd(fqdn, 'status.diskusage')
            data['diskTotal'] = float(ret[ret.keys()[0]]['/']['total']) / 1024.0**3
            data['diskUsed'] = (float(ret[ret.keys()[0]]['/']['total']) - float(ret[ret.keys()[0]]['/']['available'])) / 1024.0**3
            data['diskPercent'] = int(( data['diskUsed'] * 100 ) / data['diskTotal'])
            return data
        else:
            return none


    def open_firewall(self, ip):
        client = salt.client.LocalClient()
        client.cmd(settings.KVMATE_SALTCERT, 'iptables.append', ['filter', 'web', '-s ' + ip + '-j ACCEPT'])


    def update_kernel_stuff(self):
        client = salt.client.LocalClient()
        client.cmd('yesguy.server.selfnet.de','cmd.run', ['wget  http://mirror.selfnet.de/debian/dists/stable/main/installer-amd64/current/images/netboot/debian-installer/amd64/linux -O /tmp/linux', '/tmp'])
        client.cmd('yesguy.server.selfnet.de', 'cmd.run', ['wget  http://mirror.selfnet.de/debian/dists/stable/main/installer-amd64/current/images/netboot/debian-installer/amd64/initrd.gz -O /tmp/initrd.gz','/tmp'])
        client.cmd('wiseguy.server.selfnet.de', 'cmd.run', ['wget  http://mirror.selfnet.de/debian/dists/stable/main/installer-amd64/current/images/netboot/debian-installer/amd64/linux -O /tmp/linux','/tmp'])
        client.cmd('wiseguy.server.selfnet.de','cmd.run', ['wget  http://mirror.selfnet.de/debian/dists/stable/main/installer-amd64/current/images/netboot/debian-installer/amd64/initrd.gz -O /tmp/initrd.gz','/tmp'])


    def create_snapshot(self, hostname):
        host = Host.objects.filter(hostname=hostname)[0]
        s = salt.client.LocalClient()
        ret = s.cmd(host.hyper+'.server.selfnet.de', 'cmd.run', ['lvcreate -L5G -s -n snap_'+hostname+' /dev/lvm/'+hostname,'/tmp/'])
        return str(ret)

    def delete_snapshot(self, hostname):
        host = Host.objects.filter(hostname=hostname)[0]
        s = salt.client.LocalClient()
        ret = s.cmd(host.hyper+'.server.selfnet.de', 'cmd.run', ['lvremove --force lvm/snap_'+hostname, '/tmp/'])
        return str(ret)
