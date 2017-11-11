from django.conf.urls import url, include
from api import avatar_views
from django.conf.urls.static import static
from rest_framework import routers
import views
from rest_framework.authtoken import views as auth_views
from api.views import UserViewSet, CategoryViewSet, FoodItemViewSet, FoodRecordViewSet, ProfileDataViewSet, StudyViewSet, CustomTextViewSet
import api.views as api_views
from SaltTrackerService import settings
from api import ui_views

router = routers.DefaultRouter()
router.register(r'user', UserViewSet, base_name="user")
router.register(r'category', CategoryViewSet, base_name="category")
router.register(r'fooditem', FoodItemViewSet, base_name="fooditem")
router.register(r'foodrecord', FoodRecordViewSet, base_name="foodrecord")
router.register(r'profiledata', ProfileDataViewSet, base_name="profiledata")
router.register(r'custom-text', CustomTextViewSet, base_name="custom_text")
router.register(r'study', StudyViewSet, base_name="study")

urlpatterns = [
     url(r'^', include(router.urls)),
     url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
     url(r'^api-token-auth/', auth_views.obtain_auth_token),
     url(r'^fcm/', include('drf_fcm.urls')),
     url(r'profiledata/by_type/(?P<type>.+)/', api_views.get_profile_data_per_type),
     url(r'profiledata/add/batch/', api_views.add_profile_data_batch),
     url(r'profiledata/update/batch/', api_views.update_profile_data_batch),
     url(r'fooditem/by_category/(?P<pk>[0-9]+)/$', api_views.get_food_items_per_category),
     
     url(r'fooditem/by_name/(?P<name>.+)/', api_views.product_by_name_like),
     url(r'fooditem/get/recent/', api_views.get_recent_food_items),
     url(r'foodrecord/add/batch/all-nutrients/$', api_views.add_food_records_all_nutrients),
     url(r'foodrecord/add/batch/$', api_views.add_food_records),
     url(r'foodrecord/add/supplement/batch/', api_views.add_food_records_supplements),
     url(r'fooditem/get/supplements/', api_views.get_food_item_supplements),
     url(r'foodrecord/get/dates/', api_views.get_food_record_dates),
     url(r'foodrecord/by_day/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/', api_views.get_food_record_per_day),
     url(r'user/get/initial_data/foodtracker/', api_views.get_initial_user_data_food_tracker),
     url(r'user/get/initial_data/', api_views.get_initial_user_data),
     url(r'foodrecord/results/protocols', api_views.checklist_results_protocols),
     url(r'foodrecord/results/minimal/', api_views.food_tracker_results),
     url(r'foodrecord/results/categories', api_views.checklist_results_categories),
     url(r'foodrecord/results/all', api_views.checklist_results),
     url(r'shopping/results/all', api_views.shopping_results),
     url(r'user/check_email/(?P<email>.+)/', api_views.check_unique_email),
     url(r'user/check_username/(?P<username>.+)/', api_views.check_unique_username),
     url(r'user/check/cumulus/active', api_views.is_connected_to_mconnect),
     url(r'studyday/close/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/', api_views.close_day),
     url(r'studyday/delete/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/', api_views.delete_day),
     url(r'user/get/regression-model-data/(?P<model_type>[0-9]{1,2})/(?P<user_category>[a-e]{1})', api_views.get_regression_model_data),
     url(r'user/get/salt-source/', api_views.salt_intake_source),
     url(r'user/get/export-paper-app-study/', ui_views.paper_salt_study),
     url(r'user/get/user-demographics/', ui_views.user_demographics),
     url(r'user/get/user-survey/', ui_views.user_surveys),
     url(r'user/get/export/all/', ui_views.export_all),

     #avatar urls
     url(r'avatar/state/$', avatar_views.get_avatar_levels),
     url(r'avatar/data/get/$', avatar_views.get_avatar_data),
     url(r'avatar/data/update/$', avatar_views.update_avatar_data),
     url(r'avatar/sample-page/$', avatar_views.avatar_sample_page),
     url(r'avatar/missing-info/$', avatar_views.add_missing_nutrition_info),

     #push_notifications
     url("device/post-push-notif-data/$", api_views.post_push_notif_data, name='post_push_notif_data'),
     url("user/send/push-notifications/$", api_views.check_push_notifications, name='check_push_notifications'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

