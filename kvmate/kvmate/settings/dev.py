from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'b2&@-tf$*z&#tnq^iuyj+(5wsr-^-xw4tdgk(g4z1p6+zbj@62p'

INSTALLED_APPS += ('django_extensions', )

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'sqlite3.db',
    }
}

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
    }
}
