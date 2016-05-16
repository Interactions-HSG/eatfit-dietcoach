from __future__ import absolute_import

from celery import shared_task, task
from celery.task.base import periodic_task
from celery.schedules import crontab


@periodic_task(run_every=(crontab(minute='*/2')), name="some_task")
def add():
    return "hello"


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)