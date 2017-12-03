import views
from rest_framework import routers
import NutritionService
from rest_framework.authtoken import views as auth_views
from django.conf.urls import url, include

router = routers.DefaultRouter()

urlpatterns = [
     url(r'^', include(router.urls)),
     url(r'^products/(?P<gtin>\d{0,50})/$', NutritionService.views.get_product),
     url(r'^update', NutritionService.views.update_database),
]
