from .dev import * # set your production settings here
from .create import *
from .vnc import *

try:
    from .local_settings import *
except ImportError:
    print('No local settings found')
