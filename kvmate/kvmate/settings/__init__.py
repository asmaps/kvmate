import os
import logging

if os.environ.get('PROD'):
    logging.info('Using production settings')
    from .production import *
else:
    from .dev import *

try:
    from .local_settings import *
except ImportError:
    print('No local settings found')

from django.conf import ImproperlyConfigured
if not SECRET_KEY:
    raise ImproperlyConfigured('please generate a SECRET_KEY and add it to your local settings')