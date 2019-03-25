import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EatFitService.settings')

app = Celery('EatFitService')
app.config_from_object('django.conf:local_settings', namespace='CELERY')
app.autodiscover_tasks()
