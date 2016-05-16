"""
Definition of urls for EatFitService.
"""

from django.conf.urls import patterns, url, include
from rest_framework import routers
import views
from rest_framework.authtoken import views as auth_views
from TrustBoxAPI.product_views import ProductViewSet
from TrustBoxAPI import product_views

router = routers.DefaultRouter()
router.register(r'product', ProductViewSet, base_name="product")

urlpatterns = [
     url(r'^', include(router.urls)),
     url(r'^product/bygtin/(?P<gtin>[0-9]+)', product_views.product_by_gtin),
     url(r'^product/byname/(?P<name>.+)', product_views.product_by_name),
     url(r'^product/importlog/all', product_views.import_log_all),
     url(r'^product/importlog/latest', product_views.import_log_latest),
     url(r'fill/', views.fill_db),
     url(r'celery/', views.test_celery),
     url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
     url(r'^api-token-auth/', auth_views.obtain_auth_token)
]
