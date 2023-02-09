"""
Django settings for swarm_server project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import datetime
import logging
import time
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-3g(mukqkj_e2hp(l*8*)0alqcm+9_5*xv&)30ne%&h2z$yzify'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '10.0.0.128']


# Application definition

INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'huey.contrib.djhuey',
    'swarm.apps.SwarmConfig',
    'channels',
]

ATOMIC_REQUESTS = True

CORS_ALLOWED_ORIGINS = ['http://localhost', 'http://localhost:3000', 'http://localhost:8000']
CSRF_TRUSTED_ORIGINS = ['http://localhost', 'http://localhost:3000']

DISABLED_INSTAGRAM_TIMEOUT       = datetime.timedelta(hours=1, minutes=30)
DISABLED_INSTAGRAM_TIMEOUT_LONG  = datetime.timedelta(days=2)
DISABLED_INSTAGRAM_TIMEOUT_PERM  = datetime.timedelta(weeks=52 * 100)

# After failing to login this many times in a row, the account will be relogged on every subsequent try, until
# login starts to work again (which - to be clear - could be never, e.g. if the username / pw is incorrect)
ERRORS_BEFORE_RELOGIN = 2

NOTIFY_EARLY = True

HUEY = {
    'name': 'mydjangoproject',
    'url': 'redis://localhost:6379/?db=1',

    # To run Huey in "immediate" mode with a live storage API, specify
    # immediate_use_memory=False.
    'immediate_use_memory': False,

    # OR:
    # To run Huey in "live" mode regardless of whether DEBUG is enabled,
    # specify immediate=False.
    'immediate': False,

    'consumer': {
        'workers': 3,
    }
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'swarm_server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'build'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'swarm_server.wsgi.application'
ASGI_APPLICATION = "swarm_server.asgi.application"
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = 'collectstatic/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ORIGIN_WHITELIST = ['http://localhost', 'http://localhost:3000', 'http://localhost:8000']


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname:<8s} {asctime}.{msecs:0<3.0f} [{name:^25s}] - {message}',
            'datefmt': '%d/%m/%y %H:%M:%S',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.FileHandler',
            'encoding': 'utf8',
            'formatter': 'verbose',
            'filename': 'scrape_elegy.log',
            'level': 'DEBUG'
        },
        'mail_admins': {
            'level': 'CRITICAL',
            'class': 'swarm.handlers.EmailHandler'
        }
    },
    'loggers': {
        'swarm': {
            'handlers': ['console', 'file', 'mail_admins'],
            'propagate': False,
            'level': 'DEBUG'
        },
        'huey': {
            'handlers': ['console', 'file', 'mail_admins'],
            'propagate': False,
            'level': 'INFO'
        },
        'django': {
            'handlers': ['console', 'file', 'mail_admins'],
            'propagate': False,
            'level': 'INFO'
        },
        'daphne': {
            'handlers': ['console', 'file', 'mail_admins'],
            'propagate': False,
            'level': 'INFO'
        },
    }
}



HOME_ROOM_GROUP_NAME = 'frontend_stream'
AUDIO_ROOM_GROUP_NAME = 'audio_stream'

# Amount of time to add for people in the exhibition to chill BEFORE the audiostream start playing
DELAY_START = datetime.timedelta(0)

# Amount of time to add for people in the exhibition to chill AFTER the audiostream ends, before we allow the next user to enter their deets
# This turns out to be about 7 seconds less than it should be...
DELAY_END = datetime.timedelta(seconds=15)

# For the purpose of displaying the ETA to the user - Amount of time to add to our estimation of how long the
# audiostream takes (before we get a more accurate reading)
TIME_GUESS_BUFFER = datetime.timedelta(seconds=30)

# Email stuff

ADMINS = [('Misha Mikho', 'mvmikho@gmail.com')]
EMAIL_USE_TLS = True
EMAIL_PORT = 587

# Secrets ;) ;)

from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

AZURE_SPEECH_KEY = os.environ['AZURE_SPEECH_KEY']
AZURE_SPEECH_REGION = os.environ['AZURE_SPEECH_REGION']

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ['EMAIL_HOST']
SERVER_EMAIL = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']