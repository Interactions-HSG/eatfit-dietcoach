"""
Definition of urls for EatFitService.
"""

from django.conf.urls import url, include
from django.urls import path
from django.contrib import admin
from rest_framework.authtoken import views as auth_views


# Uncomment the next lines to enable the admin:
# from django.conf.urls import include
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    url(r'', include('NutritionService.urls')),
    #url(r'', include('TrustBoxAPI.urls')),
    url(r'', include('SaltTrackerService.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', auth_views.obtain_auth_token),
    path('admin/', admin.site.urls)
]
