from __future__ import absolute_import

from celery import shared_task, task
from celery.task.base import periodic_task
from celery.schedules import crontab
from TrustBoxAPI import trustbox_connector


@shared_task
def add(x,y):
    return "hello"

@shared_task
def get_trustbox_data_by_call():
    trustbox_connector.load_changed_data()

#@periodic_task(run_every=(crontab(minute=0, hour=2)), name="get_trustbox_data")
def get_trustbox_data():
    trustbox_connector.load_changed_data()