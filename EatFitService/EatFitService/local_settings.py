from EatFitService.settings import *

CELERY_BROKER_URL = 'amqp://rabbitmq'

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

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s %(asctime)s %(name)s]: %(message)s',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': '/var/log/nutrition-service.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'NutritionService': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
         # Log all exceptions in logfile
        '': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True
        }
    },
}
