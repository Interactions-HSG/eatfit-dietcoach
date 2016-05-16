"""
Definition of urls for EatFitService.
"""

from django.conf.urls import patterns, url, include
from rest_framework import routers
import views

router = routers.DefaultRouter()

urlpatterns = [
     url(r'^$', include(router.urls)),
     url(r'fill/', views.fill_db),
     url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
