#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Definition of views.
"""

from django.shortcuts import render
from drf_fcm.models import Device
from drf_fcm.serializers import DeviceSerializer
from django.http import HttpRequest
from django.template import RequestContext
from django.http.response import HttpResponse
from rest_framework.decorators import permission_classes, api_view, renderer_classes, parser_classes
from rest_framework import permissions, viewsets, status
from rest_framework.response import Response
from api.models import SaltTrackerUser, Category, FoodItem, FoodRecord, ProfileData, StudyDay, Study, AutoidScraperMigrosBasketItem, FoodRecordSupplement, FoodItemSupplement, AutoidScraperMigrosItem
from api.serializer import SaltTrackerUserSerializer, CategorySerializer,CustomTextSerializer, FoodItemSerializer, ProfileDataSerializer, FoodRecordSerializer, FoodRecordCreateSaltSerializer, FoodRecordCreateSerializer, InitalUserDataSerializer, StudySerializer, FoodItemSupplementSerializer, FoodRecordSupplementSerializer
from django.contrib.auth.models import User
from rest_framework.generics import get_object_or_404
from rest_framework.renderers import JSONRenderer
from datetime import datetime
import itertools
from django.core.validators import validate_email
from datetime import date, timedelta
from api import results, regression_model_data, salt_source
from django.db.models.query_utils import Q
from django.db.models import Sum
from django.db.models.aggregates import Avg
import requests
from django.utils import translation
from django.core.cache import cache

EXCLUDED_USERS = " and u.user_id not in (17, 87);"
QUALIFYING_USER_QUERY = "SELECT * FROM salt_tracker_user as u where u.cumulus_email is not null and u.cumulus_password is not null and ((select count(*) from study_day as s where s.user_id = u.user_id and s.is_locked=1) > 3) "

@permission_classes((permissions.AllowAny,))
class UserViewSet(viewsets.ViewSet):

    def list(self, request):
        return Response(None, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, request):
        serializer = SaltTrackerUserSerializer(data=request.data)
        if serializer.is_valid():
            if User.objects.filter(username=serializer.validated_data["user"]["username"]).exists():
                return Response(None, status=status.HTTP_409_CONFLICT)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        if not request.user.is_authenticated():
            return Response(status=status.HTTP_401_UNAUTHORIZED) 
        if request.user.pk != pk:
             return Response(status=status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(SaltTrackerUser.objects.all(), pk=pk)
        serializer = SaltTrackerUserSerializer(user)
        return Response(serializer.data)

    def update(self, request, pk=None):
        if not request.user.is_authenticated():
            return Response(status=status.HTTP_401_UNAUTHORIZED) 
        if not request.user.has_perm("change_user") and not request.user.has_perm("change_salttrackeruser") and not request.user.pk == int(pk):
            return Response(status=status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(SaltTrackerUser.objects.all(), pk=pk)
        serializer = SaltTrackerUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        return Response(None, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@permission_classes((permissions.IsAuthenticated,))
class CategoryViewSet(viewsets.ViewSet):

    def list(self, request):
        categories = Category.objects.all().order_by("sort")
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        category = get_object_or_404(Category.objects.all(), pk=pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

@permission_classes((permissions.IsAuthenticated,))
class FoodItemViewSet(viewsets.ViewSet):

    def list(self, request):
        food_items = FoodItem.objects.all()
        serializer = FoodItemSerializer(food_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        food_item = get_object_or_404(FoodItem.objects.all(), pk=pk)
        serializer = FoodItemSerializer(food_item)
        return Response(serializer.data)

@permission_classes((permissions.IsAuthenticated,))
class FoodRecordViewSet(viewsets.ViewSet):

    def list(self, request):
        food_records = FoodRecord.objects.filter(user=request.user)
        serializer = FoodRecordSerializer(food_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        food_record = get_object_or_404(FoodRecord.objects.filter(user=request.user), pk=pk)
        serializer = FoodRecordSerializer(food_record)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        record = get_object_or_404(FoodRecord.objects.filter(user=request.user), pk=pk)
        record.delete()
        return Response(None, status=status.HTTP_200_OK)

@permission_classes((permissions.IsAuthenticated,))
class CustomTextViewSet(viewsets.ViewSet):
    
     def create(self, request):
        serializer = CustomTextSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data["user"] == request.user:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@permission_classes((permissions.IsAuthenticated,))
class ProfileDataViewSet(viewsets.ViewSet):

    def list(self, request):
        profile_datas = ProfileData.objects.filter(user=request.user)
        serializer = ProfileDataSerializer(profile_datas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        profile_data = get_object_or_404(ProfileData.objects.filter(user=request.user), pk=pk)
        serializer = ProfileDataSerializer(profile_data)
        return Response(serializer.data)
    
    def create(self, request):
        serializer = ProfileDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        profile_data =  get_object_or_404(ProfileData.objects.filter(user=request.user), pk=pk)
        serializer = ProfileDataSerializer(profile_data, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@permission_classes((permissions.IsAuthenticated,))
class StudyViewSet(viewsets.ViewSet):

    def list(self, request):
        studies = Study.objects.filter(user=request.user)
        serializer = StudySerializer(studies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        studies = get_object_or_404(Study.objects.filter(user=request.user), pk=pk)
        serializer = StudySerializer(product)
        return Response(serializer.data)

    def create(self, request):
        serializer = StudySerializer(data=request.data)
        Study.objects.filter(user=request.user).update(is_active=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_profile_data_per_type(request, type):
    profile_datas = ProfileData.objects.filter(user=request.user, profile_data_type=type)
    serializer = ProfileDataSerializer(profile_datas, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_food_items_per_category(request, pk):
    app_name = request.GET.get('app_name', None)
    if app_name:
        fooditems = FoodItem.objects.filter(category__pk=pk).order_by("sort")
    else:
        fooditems = FoodItem.objects.filter(category__pk=pk, show_in_foodtracker = True).order_by("sort")
    serializer = FoodItemSerializer(fooditems, many=True, context = {"show_all_supplements" : app_name})
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def add_profile_data_batch(request):
    serializer = ProfileDataSerializer(data=request.data, many=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes((permissions.IsAuthenticated,))
def update_profile_data_batch(request):
    serializer = ProfileDataSerializer(data=request.data, many=True)
    if serializer.is_valid():
        for item in serializer.validated_data:
            ProfileData.objects.update_or_create(
                profile_data_type = item["profile_data_type"], name=item["name"], user=request.user,
                defaults={'value': item["value"]})
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def add_food_records(request):
    serializer = FoodRecordCreateSaltSerializer(data=request.data, many=True)
    if serializer.is_valid():
        study = Study.objects.filter(user=request.user).order_by("-start_date")
        if not study.exists():
            return Response(serializer.data, status=status.HTTP_403_FORBIDDEN)
        dates = [r["date"] for r in serializer.validated_data]
        dates = set(dates)
        study_day = None
        for date in dates:
            study_days =  StudyDay.objects.filter(date__year=date.year,date__month=date.month,date__day=date.day, is_locked=False, user=request.user)
            if not study_days.exists():
                locked_study_days = StudyDay.objects.filter(date__year=date.year,date__month=date.month,date__day=date.day, is_locked=True, user=request.user)
                if locked_study_days.exists():
                    return Response(serializer.data, status=status.HTTP_409_CONFLICT)
                study_day = StudyDay.objects.create(date=date, is_locked=False, user=request.user, study = study[0])
            else:
                study_day = study_days[0]
        food_records = []
        for data in serializer.validated_data:
            created_item = FoodRecord.objects.create(user=request.user, daytime = data["daytime"], numberOfPortions = data["numberOfPortions"]
            , total_salt = data["total_salt"], food_item = data["food_item"], date = data["date"], study_day = study_day, added=datetime.now())
            if data.get("supplements", None):
                for supplement in data["supplements"]:
                    FoodRecordSupplement.objects.create(food_item_supplement_id = int(supplement),total_salt = float(data["supplements"][supplement]),food_record = created_item)
        return Response(None, status=status.HTTP_201_CREATED)
    print(serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def add_food_records_all_nutrients(request):
    serializer = FoodRecordCreateSerializer(data=request.data, many=True)
    if serializer.is_valid():
        study = Study.objects.filter(user=request.user)
        if not study.exists():
            return Response(serializer.data, status=status.HTTP_403_FORBIDDEN)
        dates = [r["date"] for r in serializer.validated_data]
        dates = set(dates)
        study_day = None
        for date in dates:
            study_days =  StudyDay.objects.filter(date__year=date.year,date__month=date.month,date__day=date.day, is_locked=False, user=request.user)
            if not study_days.exists():
                locked_study_days = StudyDay.objects.filter(date__year=date.year,date__month=date.month,date__day=date.day, is_locked=True, user=request.user)
                if locked_study_days.exists():
                    return Response(serializer.data, status=status.HTTP_409_CONFLICT)
                study_day = StudyDay.objects.create(date=date, is_locked=False, user=request.user, study = study[0])
            else:
                study_day = study_days[0]
        food_records = []
        for data in serializer.validated_data:
            created_item = FoodRecord.objects.create(user=request.user, daytime = data["daytime"], numberOfPortions = data["numberOfPortions"]
            , total_salt = data["total_salt"], total_sugar = data["total_sugar"], total_added_sugar = data["total_added_sugar"], total_fruit = data["total_fruit"],
            total_vegetables = data["total_vegetables"], total_alcohol = data["total_alcohol"], 
            food_item = data["food_item"], date = data["date"], study_day = study_day, added=datetime.now())
            if data.get("supplements", None):
                for supplement in data["supplements"]:
                    FoodRecordSupplement.objects.create(food_item_supplement_id = supplement["food_item_supplement"], food_record = created_item,
                                                        total_salt = supplement["total_salt"], total_sugar = supplement["total_sugar"], total_added_sugar = supplement["total_added_sugar"],
                                                        total_fruit = supplement["total_fruit"], total_vegetables = supplement["total_vegetables"], total_alcohol = supplement["total_alcohol"])
        return Response(None, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def add_food_records_supplements(request):
    serializer = FoodRecordSupplementSerializer(data=request.data, many=True)
    if serializer.is_valid():
        for data in serializer.validated_data:
            FoodRecordSupplement.objects.create(user=request.user, food_record = data["food_record"],total_salt = data["total_salt"], food_item_supplement = data["food_item_supplement"])
        return Response(None, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
@renderer_classes((JSONRenderer, ))
def get_food_record_dates(request):
    start_day = date.today() - timedelta(days=6)
    dates = StudyDay.objects.filter(user=request.user, study__is_active=True, is_locked=False, date__gte=start_day).order_by("-date").values_list("date", flat=True)
    return Response(dates, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_recent_food_items(request):
    recent_food_records = FoodRecord.objects.filter(user=request.user).order_by("-date")[:10]
    food_items = set()
    for recent_food_record in recent_food_records:
        food_items.add(recent_food_record.food_item)
    serializer = FoodItemSerializer(food_items, many=True, context = {"show_all_supplements" : app_name})
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
@renderer_classes((JSONRenderer, ))
def get_food_record_per_day(request, year, month, day):
    study_days = StudyDay.objects.filter(user=request.user, date__year=int(year), date__month=int(month), date__day=int(day))
    if study_days.exists():
        food_records = FoodRecord.objects.filter(study_day=study_days[0])
        serializer = FoodRecordSerializer(food_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(None, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes((permissions.IsAuthenticated,))
def close_day(request, year, month, day):
    study_days = StudyDay.objects.filter(user=request.user, date__year=int(year), date__month=int(month), date__day=int(day))
    if study_days.exists():
        study_day = study_days[0]
        study_day.is_locked = True
        study_day.save()
        return Response(None, status=status.HTTP_200_OK)
    return Response(None, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes((permissions.IsAuthenticated,))
def delete_day(request, year, month, day):
    study_days = StudyDay.objects.filter(user=request.user, date__year=int(year), date__month=int(month), date__day=int(day))
    if study_days.exists():
        study_day = study_days[0]
        study_day.delete()
        return Response(None, status=status.HTTP_200_OK)
    return Response(None, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_initial_user_data(request):
    users = SaltTrackerUser.objects.filter(user=request.user)
    if not users.exists():
        return Response(None, status=status.HTTP_404_NOT_FOUND)
    data = {}
    start_day = date.today() - timedelta(days=6)
    end_day = date.today() + timedelta(days=1)
    study = Study.objects.filter(user=users[0].user, is_active=True)
    study_data = None
    first_week = []
    total_number_of_days = 0
    if study.exists():
        study_data = study[0]
        study_days_all = list(StudyDay.objects.filter(user=request.user, study=study_data, is_locked=True).order_by("date"))
        total_number_of_days = len(study_days_all)
        if not study_data.is_successful:
            if len(study_days_all) > 0:
                first_day = study_days_all[0]
                for day in study_days_all:
                    if day.date > first_day.date + timedelta(days=7):
                        if len(first_week) >= 4:
                            break
                        first_day = day
                        first_week = []
                        first_week.append(day.date)
                    else:
                        first_week.append(day.date)
                        if len(first_week) == 7:
                            break
                if len(first_week) >= 4:
                    study_data.is_successful = True
                    study_data.save()
        else:
            data["average_salt"] = results.get_average_salt_per_day(request.user, 7)
        days = StudyDay.objects.filter(user=request.user, study=study_data, date__range=(start_day, end_day))
        first_week = []
        for day in days:
            first_week.append({"date" : day.date, "is_locked" : day.is_locked})
            
    data["user_data"] = users[0]
    data["study_data"] = study_data
    data["first_week"] = first_week
    data["total_days"] = total_number_of_days
    start_day = date.today() - timedelta(days=6)
    data["total_open_days"] = StudyDay.objects.filter(user=request.user, study__is_active=True, is_locked=False, date__gte=start_day).count()
    serializer = InitalUserDataSerializer(data)
    return Response(serializer.data, status=status.HTTP_200_OK)

def __send_push_notification(user, title, message):
    print("trying to send message: " + message + " to user " + user.username)
    devices = Device.objects.filter(user=user)
    devices.send_message({"notification": {"title": title, "body": message}})

def __mark_study_as_lost(study):
    study.is_lost = True
    #study.save()

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def check_push_notifications(request):
    if request.user.is_superuser:
        push_notification_title = "Swiss FoodTracker"
        latest_start_day = date.today() - timedelta(days=4)
        studies = Study.objects.filter(is_lost = False, survey_completed = False, start_date__gte=latest_start_day, user__salttrackeruser__food_tracker_user = True).select_related("user")
        for study in studies:
            study_days = StudyDay.objects.filter(study = study).order_by("date")
            study_days_count = study_days.count()
            if study_days_count > 0: #has the user already started?
                if study_days_count >=4:
                    study.is_successful = True
                    study.save()
                print(study.start_date.date())
                print(study.pk)
                days_since_start = (date.today() - study.start_date.date()).days
                print(days_since_start)
                for d in study_days:
                    print(str(d.date) + " " +  str(d.is_locked))
                if days_since_start >= 1:
                    if study.is_successful and not study.survey_completed:
                        __send_push_notification(study.user, push_notification_title, u"Für die Ernährungsanalyse noch Abschlussbefragung ausfüllen!")
                    elif study_days_count < days_since_start:
                        __send_push_notification(study.user, push_notification_title, "Leider hast Du Tag " + str(days_since_start) + " nicht rechtzeitig abgeschlossen.")
                    elif study_days_count >= days_since_start:
                        if days_since_start >=1 and not study_days[days_since_start-1].is_locked and study_days[days_since_start-1].date.date() == date.today() - timedelta(days=1):
                            __send_push_notification(study.user, push_notification_title, "Jetzt Tag " + str(days_since_start) + " abschliessen, und Tag " + str(days_since_start+1) + " beginnen!")
                        elif days_since_start >=1 and not study_days[days_since_start-1].is_locked and study_days[days_since_start-1].date.date() != date.today() - timedelta(days=1):
                            __send_push_notification(study.user, push_notification_title, "Leider hast Du Tag " + str(days_since_start) + " nicht rechtzeitig abgeschlossen.")
                            __mark_study_as_lost(study)
                        elif days_since_start >=1 and study_days[days_since_start-1].is_locked:
                            __send_push_notification(study.user, push_notification_title, "Jetzt den " + str(days_since_start+1) + ". von 4 Tagen erfassen!")
                    else:
                        __send_push_notification(study.user, push_notification_title, "Leider hast Du Tag " + str(days_since_start-2) + " nicht rechtzeitig abgeschlossen.")
                        __mark_study_as_lost(study)
            elif study.start_date.date() == date.today():
                __send_push_notification(study.user, push_notification_title, u"Jetzt Swiss FoodTracker starten & Ernährung loggen!")
        return Response(status=status.HTTP_200_OK)
    return Response(None, status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def post_push_notif_data(request):
    serializer = DeviceSerializer(data=request.data)
    if serializer.is_valid():
        Device.objects.update_or_create(user = request.user, defaults = {"reg_id" : serializer.validated_data["reg_id"],
                                                                        "device_id" : serializer.validated_data["device_id"]})
        salttrackeruser = request.user.salttrackeruser
        salttrackeruser.notification_id = serializer.validated_data["reg_id"]
        salttrackeruser.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_initial_user_data_food_tracker(request):
    users = SaltTrackerUser.objects.filter(user=request.user)
    if not users.exists():
        return Response(None, status=status.HTTP_404_NOT_FOUND)
    data = {}
    study = Study.objects.filter(user=users[0].user, is_active=True).order_by("-start_date")
    study_data = None
    total_number_of_days = 0
    if study.exists():
        study_data = study[0]
        total_number_of_days = StudyDay.objects.filter(user=request.user, study=study_data, is_locked=True).order_by("date").count()
        if not study_data.is_successful:
            if total_number_of_days >= 4:
                study_data.is_successful = True
                study_data.save()
        else:
            data["average_salt"] = results.get_average_salt_per_day(request.user, 4)
        days = StudyDay.objects.filter(user=request.user, study=study_data).order_by("date")
            
    data["user_data"] = users[0]
    data["study_data"] = study_data
    data["first_week"] = days
    data["total_days"] = total_number_of_days
    data["total_open_days"] = StudyDay.objects.filter(user=request.user, study=study_data, is_locked=False).count()
    serializer = InitalUserDataSerializer(data)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def set_study_survey_completed(request, study_id):
    study = get_object_or_404(Study.objects.filter(user = request.user), pk = study_id)
    study.survey_completed = True
    study.save()
    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def check_unique_email(request, email):
    try:
        validate_email(email)
    except:
        return Response(None, status=status.HTTP_400_BAD_REQUEST)

    users = User.objects.filter(email=email)
    if not users.exists():
        return Response(None, status=status.HTTP_200_OK)
    else:
        return Response(None, status=status.HTTP_409_CONFLICT)

@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def check_unique_username(request, username):
    users = User.objects.filter(username=username)
    if not users.exists():
        return Response(None, status=status.HTTP_200_OK)
    else:
        return Response(None, status=status.HTTP_409_CONFLICT)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
@renderer_classes((JSONRenderer, ))
def checklist_results_protocols(request):
    food_records = results.get_food_record_result(request.user)
    return Response(food_records, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
@renderer_classes((JSONRenderer, ))
def checklist_results_categories(request):
    food_records = results.get_food_record_worst_categories(request.user)
    return Response(food_records, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
@renderer_classes((JSONRenderer, ))
def checklist_results(request):
    result_dict = {}
    result_dict["category_results"] = results.get_food_record_worst_categories(request.user)
    result_dict["protocol_results"] = results.get_food_record_result(request.user)
    result_dict["daytime_results"] = results.get_total_salt_daytimes(request.user)
    return Response(result_dict, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
@renderer_classes((JSONRenderer, ))
def food_tracker_results(request):
    average_salt_all_users = cache.get("average_salt_users")
    if not average_salt_all_users:
        total_salt_users = 0
        total_users = 0
        average_salt_all_users = 0
        for user in SaltTrackerUser.objects.raw("Select u.* from salt_tracker_user as u where ((select count(*) from study_day as s where s.user_id = u.user_id and s.is_locked=1) > 3)"):
            avergae_salt = results.get_average_salt_per_day_for_study(user.user)
            total_salt_users = total_salt_users + avergae_salt
            total_users = total_users + 1
        if total_users > 0:
            average_salt_all_users = total_salt_users / total_users
        cache.set("average_salt_users", average_salt_all_users, 3600*24)
    result_dict = {}
    result_dict["average_salt_users"] = average_salt_all_users
    result_dict["protocol_results"] = results.get_food_record_result(request.user)
    result_dict["user_estimate"] = 0
    estimate = ProfileData.objects.filter(user = request.user, name = "sft_v1_s2_q11_quantifyownsaltintake")
    if estimate.exists():
        result_dict["user_estimate"] = float(estimate[0].value)
    return Response(result_dict, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
@renderer_classes((JSONRenderer, ))
def shopping_results(request):
    result_dict = {}
    volumne_of_sales = AutoidScraperMigrosBasketItem.objects.filter(autoid_scraper_migros_basket__user__pk=request.user.pk).aggregate(Sum("price"))
    user_info = ProfileData.objects.filter(Q(profile_data_type = ProfileData.SHOPPING_HABITS_DATA) | Q(profile_data_type = ProfileData.HOUSE_HOLD_DATA),Q(name='NumberOfAdultHousemates') | Q(name='MigrosShare'), user=request.user).values("name", "value")
    result_dict["category_results"] = results.get_shopping_worst_categories(request.user)
    result_dict["basket_results"] = results.get_shopping_results(request.user)
    result_dict["user_info"] = user_info
    if volumne_of_sales["price__sum"]:
        result_dict["volume_of_sales"] =  volumne_of_sales["price__sum"]
    else:
        result_dict["volume_of_sales"] = 0
    return Response(result_dict, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
@renderer_classes((JSONRenderer, ))
def product_by_name_like(request, name):
    food_items = FoodItem.objects.filter(name__icontains=name)[:15]
    serializer = FoodItemSerializer(food_items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def get_food_item_supplements(request):
    ids = request.data
    if not ids:
        return Response(None, status=status.HTTP_400_BAD_REQUEST)
    supplement_items = FoodItemSupplement.objects.filter(id__in=ids)
    serializer = FoodItemSupplementSerializer(supplement_items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def is_connected_to_mconnect(request):
    input_data = request.data

    if "cumulusEmail" in input_data and "cumulusPassword" in input_data:
        url = "https://scrapervm.northeurope.cloudapp.azure.com/cumulus/check-m-connect-credentials"

        data = {}
        data["cumulusEmail"] = input_data["cumulusEmail"]
        data["cumulusPassword"] = input_data["cumulusPassword"]

        response = requests.post(url, auth=("eatfit", "nRbUrdMUCZycQHsNv9dX"), json=data, verify=False)

        return Response(response.status_code, status=response.status_code)
    else:
        return Response(None, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_regression_model_data(request, model_type, user_category):
    if request.user.is_superuser:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="data.csv"'
        if user_category == "a":
            queryset = SaltTrackerUser.objects.raw(QUALIFYING_USER_QUERY + EXCLUDED_USERS)
        elif user_category == "b":
            queryset = SaltTrackerUser.objects.raw("SELECT u.* FROM salt_tracker_user as u, profile_data as d where u.cumulus_email is not null and u.cumulus_password is not null and d.user_id = u.user_id and d.name='NumberOfAdultHousemates' and (d.value = '0-1' or d.value = '2')  and  ((select count(*) from study_day as s where s.user_id = u.user_id and s.is_locked=1) > 3) " + EXCLUDED_USERS)
        elif user_category == "c":
            queryset = SaltTrackerUser.objects.raw("SELECT u.* FROM salt_tracker_user as u where u.cumulus_email is not null and u.cumulus_password is not null and  ((select count(*) from study_day as s where s.user_id = u.user_id and s.is_locked=1) > 3) and (select count(*) from profile_data as d where d.user_id = u.user_id and d.name='MigrosShare' and (d.value='60-80%%' or d.value='80-100%%')) > 0 and (select count(*) from profile_data as d where d.user_id = u.user_id and d.name='CumulusUsage' and (d.value='60-80%%' or d.value='80-100%%')) > 0 " + EXCLUDED_USERS)
        elif user_category == "d":
            queryset = SaltTrackerUser.objects.raw("SELECT u.* FROM salt_tracker_user as u where u.cumulus_email is not null and u.cumulus_password is not null and ((select count(*) from study_day as s where s.user_id = u.user_id and s.is_locked=1) > 3) and ((select convert(INT, d.value) from profile_data as d where d.user_id = u.user_id and d.name='EatOutwardsLunch') + (select convert(INT, d.value) from profile_data as d where d.user_id = u.user_id and d.name='EatOutwardsBreakfast') + (select convert(INT, d.value) from profile_data as d where d.user_id = u.user_id and d.name='EatOutwardsDinner')) < 10 " + EXCLUDED_USERS)
        elif user_category == "e":
            queryset = SaltTrackerUser.objects.raw("SELECT u.* FROM salt_tracker_user as u where u.cumulus_email is not null and u.cumulus_password is not null and ((select count(*) from study_day as s where s.user_id = u.user_id and s.is_locked=1) > 3) and ((select convert(INT, d.value) from profile_data as d where d.user_id = u.user_id and d.name='EatOutwardsLunch') + (select convert(INT, d.value) from profile_data as d where d.user_id = u.user_id and d.name='EatOutwardsBreakfast') + (select convert(INT, d.value) from profile_data as d where d.user_id = u.user_id and d.name='EatOutwardsDinner')) < 10 and (select count(*) from profile_data as d where d.user_id = u.user_id and d.name='MigrosShare' and (d.value='60-80%%' or d.value='80-100%%')) > 0 and (select count(*) from profile_data as d where d.user_id = u.user_id and d.name='CumulusUsage' and (d.value='60-80%%' or d.value='80-100%%')) > 0 and (select count(*) from profile_data as d where d.user_id = u.user_id and d.name='NumberOfAdultHousemates' and (d.value='0-1' or d.value='2')) > 0 " + EXCLUDED_USERS)
        else:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)
        model_type = int(model_type)
        if model_type == 1:
            response = regression_model_data.get_data_for_regression_model_1(queryset, response)
        elif model_type == 2:
            response = regression_model_data.get_data_for_regression_model_2(queryset, response)
        elif model_type == 3:
            response = regression_model_data.get_data_for_regression_model_3(queryset, response)
        elif model_type == 4:
            response = regression_model_data.get_data_for_regression_model_4(queryset, response)
        elif model_type == 5:
            response = regression_model_data.get_data_for_regression_model_5(queryset, response)
        elif model_type == 6:
            response = regression_model_data.get_data_for_regression_model_6(queryset, response)
        elif model_type == 7:
            response = regression_model_data.get_data_for_regression_model_5_custom_cat(queryset, response)
        elif model_type == 8:
            response = regression_model_data.get_data_for_regression_model_6_custom_cat(queryset, response)
        elif model_type == 9:
            response = regression_model_data.get_data_for_regression_model_1_custom_cat(queryset, response)
        elif model_type == 10:
            response = regression_model_data.get_data_for_regression_model_3_custom_cats(queryset, response)
        return response
    return Response(None, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def salt_intake_source(request):
    if request.user.is_superuser:
        users = SaltTrackerUser.objects.raw(QUALIFYING_USER_QUERY + EXCLUDED_USERS)
        for user in users:
            salt_source.mapping_results(user)
        return Response(None, status=status.HTTP_200_OK)
    return Response(None, status=status.HTTP_403_FORBIDDEN)


def __get_item_with_less_whitespace(item1, item2):
    if len(item1.name) < len(item2.name):
        return item1, item2
    else:
        return item2, item1