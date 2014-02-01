"""
Django settings for kvmate project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

HUEY = {
    'backend': 'huey.backends.redis_backend',
    'name': 'kvmate_huey',
    'connection': {'host': 'localhost', 'port': 6379},
    'always_eager': False,
    # Options to pass into the consumer when running ``manage.py run_huey``
    'consumer_options': {'workers': 4},
}

LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/logout'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'sqlite3.db',
    }
}

# Application definition
INSTALLED_APPS = (
    'kvmate',
    'host',
    'vnc',
    'huey.djhuey',
    'bootstrapform',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'kvmate.urls'

WSGI_APPLICATION = 'kvmate.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_URL = '/static/'

# Logging setup
# https://docs.djangoproject.com/en/1.6/topics/logging/
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'kvmate.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'kvmate': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'backends': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'host': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'vnc': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'huey.consumer': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
    }
}


#################
### KVMate specific settings
#################

# Create Host defaults
CREATE_HOST_DEFAULT_IP = '192.168.0.'
CREATE_HOST_DEFAULT_NETMASK = '255.255.255.0'
CREATE_HOST_DEFAULT_GATEWAY = '192.168.0.1'
CREATE_HOST_DEFAULT_DNS = '192.168.0.1'
CREATE_HOST_DEFAULT_DOMAIN = 'vm.example.com'
CREATE_HOST_DEFAULT_SETUP_SCRIPT = 'http://preseed.example.com/post_install.sh'

### Settings for the virtinstall command:
# The name of the bridge on the hypervisor the new host should use
BRIDGE_NAME = "br0"
# The type of the bridge, set it to 'bridge' for linux and to 'network' for openvswitch
BRIDGE_TYPE = "bridge"
# The name of the libvirt volume-pool that should be used
STORAGEPOOL_NAME = "virtualmachines"
# The amount of memory a new host should reserve
DISKSIZE = "5"
# the final ip/dns name of your instance used for the preseed downloads
PRESEED_HOST = "preseed.example.com"
# Where the preseedfiles will be stored and downloaded (serve this directory statically for your virtual machines)
PRESEEDPATH = "/home/kvmate/preseed/"
# A url where the latest netinstaller is available
NETINSTALL_URL = "http://ftp.de.debian.org/debian/dists/wheezy/main/installer-amd64/"
# the port where the preseedfiles can be downloaded
# !!! IMPORTANT: this port may not redirect to https, as the debian installer's wget does not support ssl !!!
PRESEED_PORT = "80"

### Settings for the preseeding process:
DEFAULT_MIRROR = "ftp.de.debian.org"
DEFAULT_TIMEZONE = "Europe/Berlin"
DEFAULT_NTPSERVER = "0.europe.pool.ntp.org"
INITIAL_PASSWORD = "geheim42"

VNC_HOST = '127.0.0.1'
