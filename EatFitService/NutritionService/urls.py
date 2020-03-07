from NutritionService.views import views, crowdsource_views, utils_view
from NutritionService import legacy_views
from rest_framework import routers
import NutritionService

from django.conf.urls import url, include
from django.views.decorators.cache import cache_page

router = routers.DefaultRouter()

urlpatterns = [
     url(r'^', include(router.urls)),
     url(r'^products/(?P<gtin>\d{0,50})/$', cache_page(3600)(NutritionService.views.views.get_product)),

     url(r'^products/better-products/(?P<gtin>\d{0,50})/', NutritionService.views.views.get_better_products_gtin),
     url(r'^products/better-products/category/(?P<minor_category_pk>\d+)/', NutritionService.views.views.get_better_products_minor_category),
     url(r'^product/report/$', views.report_product),
     url(r'^product/missing/$', views.report_missing_gtin),

     url(r'^crowdsource/product/$', crowdsource_views.create_crowdsouce_product),
     url(r'^crowdsource/products/$', crowdsource_views.get_all_crowdsource_products),
     url(r'^crowdsource/product/(?P<gtin>\d{0,50})/$', crowdsource_views.handle_crowdsouce_product),  # GET or PUT
     url(r'^crowdsource/approve/$', crowdsource_views.approve_crowdsouce_products),

     url(r'^health-tipps/$', views.get_health_tipps),
     url(r'^current-studies/$', views.CurrentStudiesView.as_view(), name='current-studies'),

     url(r'^category/major/$', views.get_major_categories),
     url(r'^category/minor/$', views.get_minor_categories),

     url(r'^report/daily-report/$', views.generate_status_report),

     url(r'^data/data-cleaning/$', views.data_clean_task),

     url(r'^receipt2nutrition/send-receipts/$', views.SendReceiptsView.as_view(), name='send-receipts'),
     url(r'^receipt2nutrition/send-receipts-experimental/$', views.send_receipts_experimental,
         name='send-receipts-experimental'),
     url(r'^receipt2nutrition/basket-analysis/$', views.BasketAnalysisView.as_view(), name='basket-analysis'),
     url(r'^receipt2nutrition/export/receipts/$', views.export_digital_receipts),
     url(r'^receipt2nutrition/export/matching/$', views.export_matching),

     url(r'^tools/$', utils_view.UtilsList.as_view(), name='tools'),
     url(r'^tools/import-allergens/$', utils_view.AllergensView.as_view(), name='import-allergens'),
     url(r'^tools/import-nutrients/$', utils_view.NutrientsView.as_view(), name='import-nutrients'),
     url(r'^tools/import-products/$', utils_view.ProductsView.as_view(), name='import-products'),

     url(r'^update', NutritionService.views.views.update_database),
     url(r'^products/from-openfood/', NutritionService.views.views.get_products_from_openfood),
     url(r'^products/from-codecheck/', NutritionService.views.views.get_products_from_codecheck),
     url(r'^products/calculate-ofocm/', NutritionService.views.views.calculate_ofcom_values),
     url(r'^legacy/import-missing-trustbox/$', legacy_views.import_missing_products),
     url(r'^legacy/import-trustbox/$', legacy_views.import_trustbox_products),
     url(r'^legacy/import-categories/$', legacy_views.import_categories),
     url(r'^legacy/categorize-products/$', legacy_views.categorize_products),
]
