from EatFitService.settings import *
import os

CELERY_BROKER_URL = 'amqp://rabbitmq'

# we need eager mode for testing, because logic is in tasks
CELERY_TASK_ALWAYS_EAGER = os.getenv('CELERY_DRY_RUN', False) in ['True', 'true']

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'NutritionDB',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': 'mysql',
        'PORT': '3306',
    }
}

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(name)s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/nutrition-service.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'NutritionService': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        # Log all exceptions in logfile
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True
        },
        'django.db.backends':{
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        }
    },
}
