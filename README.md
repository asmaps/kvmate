KVMate
======
KVMate is a webapp written in Django to ease the management of virtual machines. It is using libvirt to
control a number of hypervisors.

### Features
* turning virtual machines on and off
* creation and deletion of hosts
* access via VNC consoles
* a number of stats
* (optional) LDAP support
* (optional) provisioning via [Salt](https://github.com/saltstack)

### A word on its origins
This repository contains a clean rewrite of a project I started at [Selfnet](https://github.com/selfnet). 
Now this project is being replaced by a more extensive system for managing all of our servers, 
including physical ones.
