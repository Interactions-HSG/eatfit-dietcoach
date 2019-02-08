"""
Django settings for EatFitService project.

Generated by 'django-admin startproject' using Django 1.9.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""
from __future__ import absolute_import
import os
import posixpath
from os import path
from . import local_settings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7a3ff875-85c2-41eb-be28-aa5ad3d284b9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = local_settings.DEBUG
USE_DEBUG_DB = local_settings.USE_DEBUG_DB

TRUSTBOX_USERNAME = "autoidlabs_admin"
TRUSTBOX_PASSWORD = "1p$H@-!6m0"
TRUSTBOX_URL = "http://trustbox.stepcom.ch/trustBox/WS?wsdl"

REEBATE_URL = "https://autoidlabs.reebate.net:8443/shoco/receipts"
REEBATE_USERNAME = "klauslfuchs"
REEBATE_PASSWORD = "autoidlabs"

ALLOWED_HOSTS = [    
    'localhost',
    '*',
]


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

# Application definition

INSTALLED_APPS = [
    'django_cleanup',
    'rest_framework',
    'rest_framework.authtoken',
    'NutritionService',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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

if USE_DEBUG_DB:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    DATABASES = local_settings.DATABASES


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
    }
}

EMAIL_USE_SSL = True
SERVER_EMAIL = 'contact@holo-one.com'
EMAIL_HOST = 'asmtp.mail.hostpoint.ch'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'contact@holo-one.com'
EMAIL_HOST_PASSWORD = 'martyMcFly1985'
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

STATIC_URL = '/static/'

#STATIC_ROOT = posixpath.join(*(BASE_DIR.split(os.path.sep) + ['static']))
STATIC_ROOT = path.join(BASE_DIR, 'static').replace('\\', '/')


MEDIA_URL = '/media/'

MEDIA_ROOT = path.join(BASE_DIR, 'media').replace('\\', '/')


CELERY_BROKER_URL = 'amqp://localhost'
