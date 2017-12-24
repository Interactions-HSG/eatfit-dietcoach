import views
from NutritionService import legacy_views
from rest_framework import routers
import NutritionService
from rest_framework.authtoken import views as auth_views
from django.conf.urls import url, include

router = routers.DefaultRouter()

urlpatterns = [
     url(r'^', include(router.urls)),
     url(r'^products/(?P<gtin>\d{0,50})/$', NutritionService.views.get_product),
     url(r'^update', NutritionService.views.update_database),
     url(r'^products/from-openfood/', NutritionService.views.get_products_from_openfood),
     url(r'^legacy/import-missing-trustbox/$', legacy_views.import_missing_products),
     url(r'^legacy/import-trustbox/$', legacy_views.import_trustbox_products),
     url(r'^legacy/import-categories/$', legacy_views.import_categories),
     url(r'^legacy/categorize-products/$', legacy_views.categorize_products),
]
