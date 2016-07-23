from __future__ import absolute_import

from celery import shared_task, task
from celery.task.base import periodic_task
from celery.schedules import crontab
from TrustBoxAPI import trustbox_connector, category_handler
from SaltTrackerService import result_calculation
from SaltTrackerService.models import SaltTrackerUser


@shared_task
def add(x,y):
    return "hello"

@task
def get_trustbox_data_by_call():
    trustbox_connector.load_changed_data()

@task
def map_categories_to_gtin(iteration):
    category_handler.map_categories(iteration)

@task
def update_shopping_results():
    users = SaltTrackerUser.objects.using("salttracker").filter(cumulus_email__isnull=False, cumulus_password__isnull=False)
    for user in users:
        result_calculation.calculate_shopping_results(user)
