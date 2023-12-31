"""
Django settings for EatFitService project.

Generated by 'django-admin startproject' using Django 1.9.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""
from __future__ import absolute_import, print_function
import sys
import os
import posixpath
from os import path

try:
    from EatFitService.settings_keys import *
except ImportError:
    print("Please create settings_keys.py file")
    sys.exit(-1)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

DEBUG = False

ALLOWED_HOSTS = ['*']

TRUSTBOX_URL = "http://trustbox.stepcom.ch/trustBox/WS?wsdl"

REEBATE_URL = "https://autoidlabs.reebate.net:8443/shoco/receipts"

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Application definition

INSTALLED_APPS = [
    'django_cleanup',
    'rest_framework',
    'rest_framework.authtoken',
    'NutritionService',
    'storages',
    'crispy_forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'applicationinsights.django.ApplicationInsightsMiddleware',
]

ROOT_URLCONF = 'EatFitService.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'EatFitService.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'NutritionDB',
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': path.join(BASE_DIR, 'cache').replace('\\', '/'),
        'TIMEOUT': 3600,  # Timeout in secs to invalidate cache entries
        'OPTIONS': {
            'MAX_ENTRIES': 10000  # max number of cache entries, before cleanup
        }
    }
}

EMAIL_USE_SSL = True
SERVER_EMAIL = 'contact@holo-one.com'
EMAIL_HOST = 'asmtp.mail.hostpoint.ch'
EMAIL_PORT = 465
DEFAULT_FROM_EMAIL = SERVER_EMAIL
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/


STATIC_ROOT = path.join(BASE_DIR, 'static').replace('\\', '/')


MEDIA_ROOT = path.join(BASE_DIR, 'media').replace('\\', '/')


CELERY_BROKER_URL = 'amqp://localhost'


APPLICATION_INSIGHTS = {
    'ikey': APPINSIGHTS_IKEY,
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(name)s: %(message)s',
        },
    },
    'handlers': {
        'appinsights': {
            'level': 'WARNING',
            'class': 'applicationinsights.django.LoggingHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'NutritionService': {
            'handlers': ['appinsights'],
            'level': 'WARNING',
            'propagate': True,
        },
         # Log all exceptions in logfile
        '': {
            'handlers': ['appinsights'],
            'level': 'ERROR',
            'propagate': True
        }
    },
}

DEFAULT_FILE_STORAGE = 'EatFitService.azure_storage_backend.AzureMediaStorage'
STATICFILES_STORAGE = 'EatFitService.azure_storage_backend.AzureStaticStorage'

STATIC_URL = 'https://eatfitmedias.blob.core.windows.net/static/'
MEDIA_URL = 'https://eatfitmedias.blob.core.windows.net/media/'

