from NutritionService.views import views, crowdsource_views
from NutritionService import legacy_views
from rest_framework import routers
import NutritionService
from django.conf.urls import url, include

router = routers.DefaultRouter()

urlpatterns = [
     url(r'^', include(router.urls)),

     url(r'^products/(?P<gtin>\d{0,50})/$', NutritionService.views.views.get_product),
     url(r'^products/better-products/(?P<gtin>\d{0,50})/', NutritionService.views.views.get_better_products),
     url(r'^product/report/$', views.report_product),
     url(r'^product/missing/$', views.report_missing_gtin),

     url(r'^crowdsource/product/$', crowdsource_views.create_crowdsouce_product),
     url(r'^crowdsource/products/$', crowdsource_views.get_all_crowdsource_products),
     url(r'^crowdsource/product/(?P<gtin>\d{0,50})/$', crowdsource_views.handle_crowdsouce_product),  # GET or PUT
     url(r'^crowdsource/approve/$', crowdsource_views.approve_crowdsouce_products),

     url(r'^update', NutritionService.views.views.update_database),
     url(r'^products/from-openfood/', NutritionService.views.views.get_products_from_openfood),
     url(r'^products/from-codecheck/', NutritionService.views.views.get_products_from_codecheck),
     url(r'^products/calculate-ofocm/', NutritionService.views.views.calculate_ofcom_values),
     url(r'^legacy/import-missing-trustbox/$', legacy_views.import_missing_products),
     url(r'^legacy/import-trustbox/$', legacy_views.import_trustbox_products),
     url(r'^legacy/import-categories/$', legacy_views.import_categories),
     url(r'^legacy/categorize-products/$', legacy_views.categorize_products),
]
