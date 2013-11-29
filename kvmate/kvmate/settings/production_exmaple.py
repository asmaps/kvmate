from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'b2&@-tf$*z&#tnq^%b6+(5wsr-^-xw4tdgk(g4z1p6+zbj@62p'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'kvmate',
        'USER': 'kvmate',
        'PASSWORD': 'somthing_secure',
        'HOST': '127.0.0.1'
    }
}

# Logging setup
# https://docs.djangoproject.com/en/1.6/topics/logging/
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/kvmate/kvmate.log',
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
