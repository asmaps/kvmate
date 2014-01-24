from .base import INSTALLED_APPS

DEBUG = True
TEMPLATE_DEBUG = True

# SECURITY WARNING: do not use this for production!
SECRET_KEY = 'b2&@-tf$*z&#tnq^iuyj+(5wsr-^-xw4tdgk(g4z1p6+zbj@62p'

INSTALLED_APPS += ('django_extensions', )

VIRTUALIZATION_BACKEND = 'backends.dummy_backend.DummyLibvirtBackend'
