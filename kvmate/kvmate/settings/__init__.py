import os
import logging

if os.environ['PROD']:
    logging.info('Using production settings')
    from .production import *
else:
    from .dev import *
from .create import *
from .vnc import *

try:
    from .local_settings import *
except ImportError:
    print('No local settings found')
