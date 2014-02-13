from .base import LOGGING

# no debugging
DEBUG = False

# set logging verbosity
LOGGING['handlers']['file']['level'] = 'INFO'
LOGGING['handlers']['file']['filename'] = '../logs/kvmate.log'

VIRTUALIZATION_BACKEND = 'backends.mylibvirt.LibvirtBackend'
