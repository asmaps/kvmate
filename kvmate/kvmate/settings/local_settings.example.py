# copy this file to local_settings.py and modify your personal settings. Will be ignored by git

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

# generate key with `pwgen -s 64 1`
SECRET_KEY = ''


# the final ip/dns name of your instance used for the preseed downloads
PRESEED_HOST = "preseed.example.com"

# initial password set in new VMs
INITIAL_PASSWORD = "geheim42"

# Where should the in-browser VNC client connect to (probably your server's IP)
VNC_HOST = '127.0.0.1'

# defaults on host create page
CREATE_HOST_DEFAULT_DOMAIN = 'vm.example.com'
CREATE_HOST_DEFAULT_SETUP_SCRIPT = 'http://preseed.example.com/post_install.sh'