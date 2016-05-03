"""
Definition of urls for EatFitService.
"""

from django.conf.urls import url, include
import django.contrib.auth.views


# Uncomment the next lines to enable the admin:
# from django.conf.urls import include
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    url(r'', include('TrustBoxAPI.urls')),
]
