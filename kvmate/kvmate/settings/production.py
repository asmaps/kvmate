from .base import LOGGING

import os

# no debugging
DEBUG = False

# set logging verbosity
LOGGING['handlers']['file']['level'] = 'INFO'
LOGGING['handlers']['file']['filename'] = os.path.expanduser('~/logs/kvmate.log')

VIRTUALIZATION_BACKEND = 'backends.mylibvirt.LibvirtBackend'
