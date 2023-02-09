from .settings import *

DEBUG = False




print("----- USING PROD SETTINGS -----")

ADMINS = [('Misha Mikho', 'mvmikho@gmail.com'), ('Gabby Bush', 'gabby.bush@unimelb.edu.au'), ]

HUEY = {
    'name': 'scrape_elegy',
    'url': 'redis://redis:6379/?db=1',
    'consumer': {
        'workers': 3,
    }
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('redis', 6379)],
        },
    },
}

LOGGING['handlers']['file']['filename'] = 'log/scrape_elegy.log'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('POSTGRES_NAME'),
#         'USER': os.environ.get('POSTGRES_USER'),
#         'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
#         'HOST': 'db',
#         'PORT': 5432,
#     }
# }
