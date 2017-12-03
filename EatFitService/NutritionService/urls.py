import views
import NutritionService
from rest_framework.authtoken import views as auth_views
from django.conf.urls import url

urlpatterns = [
     url(r'^products/(?P<gtin>\d{0,50})/$', NutritionService.views.get_product),
     url(r'^update', NutritionService.views.update_database),
]
