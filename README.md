KVMate
======
KVMate is a webapp written in Django to ease the management of virtual machines. It is using libvirt to
interact with the hypervisor.

### Features
##### done:
* turning virtual machines on and off
* creation of hosts
* access via VNC consoles
* a number of stats
* uses AJAX wherever it makes sense

##### missing:
* tutorials on deploying and extending this thing (doc in general)
* deletion of hosts
* editing and enforcing said stats
* (optional) LDAP support, possibly with a fine-grained permission system
* (optional) provisioning via [Salt](https://github.com/saltstack)

### Feature ideas
* Support more backends (like XEN or OpenVZ)
* Live migration of VMs between physical hosts

### License
This project includes a [LICENSE](LICENSE) file which applies to all code written for this project 
(MIT license, in short). 

The subdirectory [kvmate/vnc/static/vnc/include](kvmate/vnc/static/vnc/include) however is taken
striaght and unmodified from the [noVNC](https://github.com/kanaka/noVNC/blob/master/LICENSE.txt)
project and their licenses apply. Thanks to them for providing a core feature of KVMate.

It is also appropriate to thank the guys from [Twitter's Bootstrap](http://getbootstrap.com/components/)
and [Glyphicons](http://glyphicons.com/) for providing an awesome framework for non-designers like
us to make stuff pretty.

### A word on its origins
This repository contains a clean rewrite of a project [Daniel Nägele](https://github.com/danieljn) started at [Selfnet](https://github.com/selfnet). 
Now this project is being replaced by a more extensive system for managing all of our servers including non-virtual ones.
