from EatFitService.settings import *

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
