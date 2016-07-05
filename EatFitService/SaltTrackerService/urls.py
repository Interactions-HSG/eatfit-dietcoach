"""
Definition of urls for EatFitService.
"""

from django.conf.urls import patterns, url, include
from rest_framework import routers
import views
from SaltTrackerService import views

router = routers.DefaultRouter()

BASE_URL = r"^salt-tracker/"

urlpatterns = [
     url(BASE_URL, include(router.urls)),
     url(BASE_URL + "test", views.test),
]
