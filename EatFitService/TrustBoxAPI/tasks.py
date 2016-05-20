from __future__ import absolute_import

from celery import shared_task, task
from celery.task.base import periodic_task
from celery.schedules import crontab
from TrustBoxAPI import trustbox_connector, category_handler


@shared_task
def add(x,y):
    return "hello"

@task
def get_trustbox_data_by_call():
    trustbox_connector.load_changed_data()

@task
def map_categories_to_gtin():
    category_handler.map_categories()