from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'b2&@-tf$*z&#tnq^%b6+(5wsr-^-xw4tdgk(g4z1p6+zbj@62p'

INSTALLED_APPS += ( 'django_extensions', )

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'kvmate',
        'USER': 'kvmate',
        'PASSWORD': 'whatever',
        'HOST': '127.0.0.1'
    }
}
