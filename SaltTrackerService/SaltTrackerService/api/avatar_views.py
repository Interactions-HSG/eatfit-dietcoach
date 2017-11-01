from rest_framework.decorators import api_view, permission_classes
from api.models import FoodRecordSupplement
from api.models import SaltTrackerUser
from django.db.models.query_utils import Q
from api.models import AvatarTip
from api.models import AvatarLog
from django.core.cache import cache
from django.shortcuts import render
from api.serializer import AvatarDataSerializer
from api.models import AvatarData
from datetime import datetime
from django.db.models.aggregates import Sum
from api.models import FoodRecord
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import permissions
from django.db import connection

NUMBER_OF_DAYS_BACK = 4.0 # defines how many tracked days the avatar takes into accound
AVATAR_DATA_CACHE_POSTFIX = "_avatar_data"
AVATAR_LOG_MESSAGE = "show_avatar"


def avatar_sample_page(request):
    key = request.GET.get("key", "")
    return render(request, "avatar/avatar.html", {"key" : key})


@api_view(['POST']) # function for updating the avatar data (e.g. hair_type)
@permission_classes((permissions.IsAuthenticated,))
def update_avatar_data(request):
    serializer = AvatarDataSerializer(data=request.data)
    if serializer.is_valid():
        AvatarData.objects.update_or_create(user = request.user, defaults = serializer.validated_data)
        return Response(status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# function for retrieving the avatar data values (e.g. hair_type) in JSON format	
@api_view(['GET']) 
@permission_classes((permissions.IsAuthenticated,))
def get_avatar_data(request):
    avatar_data = get_object_or_404(AvatarData.objects.all(), user = request.user)
    serializer = AvatarDataSerializer(avatar_data)
    return Response(serializer.data, status=status.HTTP_200_OK)

# function for retrieving the avatar data values (e.g. hair_type) in JSON format	
@api_view(['GET']) 
@permission_classes((permissions.IsAuthenticated,))
def add_missing_nutrition_info(request):
    count = 0
    for record in FoodRecord.objects.all().select_related("food_item")[4000:6000]:
        try:
            supplements = FoodRecordSupplement.objects.filter(food_record = record).select_related("food_item_supplement")
            total_sugar, total_added_sugar, total_fruit, total_vegetables, total_alcohol = 0,0,0,0,0
            for supplement in supplements:
                try:
                    reference_portion_supplement = supplement.food_item_supplement.reference_portion/100.0
                    supplement.total_sugar = supplement.food_item_supplement.sugar * reference_portion
                    supplement.total_added_sugar = supplement.food_item_supplement.added_sugar * reference_portion
                    supplement.total_fruit = supplement.food_item_supplement.fruit * reference_portion
                    supplement.total_vegetables = supplement.food_item_supplement.vegetables * reference_portion
                    supplement.total_alcohol = supplement.food_item_supplement.alcohol * reference_portion
                    total_sugar = total_sugar + supplement.food_item_supplement.sugar * reference_portion
                    total_added_sugar = total_added_sugar + supplement.food_item_supplement.added_sugar * reference_portion
                    total_fruit = total_fruit + supplement.food_item_supplement.fruit * reference_portion
                    total_vegetables = total_vegetables + supplement.food_item_supplement.vegetables * reference_portion
                    total_alcohol = total_alcohol + supplement.food_item_supplement.alcohol * reference_portion
                    supplement.save()
                except:
                    pass
            reference_portion = record.food_item.reference_portion/100.0
            record.total_sugar = record.food_item.sugar * reference_portion + total_sugar
            record.total_added_sugar = record.food_item.added_sugar * reference_portion + total_added_sugar
            record.total_fruit = record.food_item.fruit * reference_portion + total_fruit
            record.total_vegetables = record.food_item.vegetables * reference_portion + total_vegetables
            record.total_alcohol = record.food_item.alcohol * reference_portion + total_alcohol
            record.save()
            print("saved record: " + str(count))
            count = count + 1
        except:
            pass
    return Response(status=status.HTTP_200_OK)


# function for retrieving + calculating the avatar ingredient and visual variables (e.g. heart_lvl, salt_lvl) in JSON format	
@api_view(['GET']) 
def get_avatar_levels(request):
    key = request.GET.get("key", "")
    tokens = Token.objects.filter(key = key).select_related("user") # compare input token with user token
    if tokens.exists(): ## if user token exists
        user = tokens[0].user
        AvatarLog.objects.create(user = user, message = AVATAR_LOG_MESSAGE, time = datetime.now())
        result_dict = {}
        result_dict["new_values"] = {}
        result_dict["old_values"] = {}
        caluculate_results, result_dict = __fetch_previous_results(user, result_dict)
        if caluculate_results:
            # get all food records, last 4 days with data
            dates = FoodRecord.objects.filter(user=user, study_day__is_locked=True, study_day__date__lt = datetime.now()).values("date").order_by("-date").annotate(Sum("total_salt"), Sum("total_added_sugar"), Sum("total_fruit"), Sum("total_vegetables"), Sum("total_alcohol"))[:NUMBER_OF_DAYS_BACK]
            nutrition_levels = {}
            count = 0
            last_day_average = 0.0
            last_day_dict = {}
		    # for each date/day
            for date in dates:
                if count == 0: # count 0 = last day
                    salt_level, added_sugar_level, fruit_and_vegetable_level, alcohol_level = __map_nutrition_levels(date, user.salttrackeruser.sex, 1)
                    last_day_average = (salt_level + added_sugar_level + fruit_and_vegetable_level + alcohol_level)/4.0
                    last_day_dict = {"Salt" : salt_level, "Sugar" : added_sugar_level, "FV" : fruit_and_vegetable_level, "Alcohol" : alcohol_level}
                    last_day_average = round(last_day_average)
                for nutrition in date:
                    if nutrition != "date" and date[nutrition] != None:
                        if not nutrition in nutrition_levels:
                            nutrition_levels[nutrition] = 0
                        nutrition_levels[nutrition] = nutrition_levels[nutrition] + date[nutrition]
                count = count + 1
            nutrient_dict, result_dict["new_values"]["visual_variables"]  = __calculate_avatar_values(nutrition_levels, last_day_average, user.salttrackeruser.sex)
            best_nutrient, worst_nutrient = __find_best_and_worst_level(nutrient_dict)
            result_dict["new_values"]["message"] = __generate_message(nutrient_dict, best_nutrient, worst_nutrient)
            result_dict["new_values"]["tips"] = __generate_tips(nutrient_dict, best_nutrient, worst_nutrient)
            result_dict["new_values"]["date"] = datetime.now().date()
            result_dict["new_values"]["ingredient_levels"] = nutrient_dict
            result_dict["new_values"]["last_day_ingredient_levels"] = last_day_dict
            result_dict["general_data"] = __fill_general_values(user)
            cache.set(user.username + AVATAR_DATA_CACHE_POSTFIX, result_dict, 24*3600*30) #cache for one month
        return Response(result_dict, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_404_NOT_FOUND)

def __calculate_avatar_values(nutrition_levels, last_day_average, gender):
    salt_level, added_sugar_level, fruit_and_vegetable_level, alcohol_level = __map_nutrition_levels(nutrition_levels, gender, NUMBER_OF_DAYS_BACK)
    overall_average = (salt_level + added_sugar_level + fruit_and_vegetable_level + alcohol_level) / 4.0
    heart_lvl = __map_visual_variable(salt_level, fruit_and_vegetable_level, 0.8)
    skin_lvl = __map_visual_variable(fruit_and_vegetable_level, 0, 1)
    teeth_lvl = __map_visual_variable(added_sugar_level, 0, 1)
    liver_lvl = __map_visual_variable(alcohol_level, 0, 1)
    mouth_lvl = __map_visual_variable(last_day_average, 0, 1)
    posture_lvl = __map_visual_variable(overall_average, 0, 1)
    tiredness_lvl = __map_visual_variable(fruit_and_vegetable_level, added_sugar_level, 0.75)
    headache_lvl = __map_visual_variable(alcohol_level, 0, 1)
    nutrient_dict = {"Salt" : salt_level, "Sugar" : added_sugar_level, "FV" : fruit_and_vegetable_level, "Alcohol" : alcohol_level, "Last Protocol" : last_day_average, "Overall" : overall_average}
    return nutrient_dict, {"heart_lvl" : heart_lvl, "skin_lvl" : skin_lvl, "teeth_lvl" : teeth_lvl, "liver_lvl" : liver_lvl,
                                                     "mouth_lvl" : mouth_lvl, "posture_lvl" : posture_lvl, "tiredness_lvl" : tiredness_lvl, "headache_lvl" : headache_lvl,
                                                     "last_day" : last_day_average, "overall" : overall_average}

def __fetch_previous_results(user, result_dict): #also checks if a calculation of the values is even necessary or if they are already cached
    cached_data = cache.get(user.username + AVATAR_DATA_CACHE_POSTFIX)
    if cached_data:
        if cached_data["new_values"]["date"] != datetime.now().date():
            result_dict["old_values"] = cached_data["new_values"]
            return True, result_dict
        else:
            result_dict = cached_data
            return False, result_dict
    else:
        return True, result_dict

def __fill_general_values(user):
    general_data = {}
    general_data["avatar_design"] = {}
    avatar_data = AvatarData.objects.filter(user = user)
    if avatar_data.exists():
        avatar_data = avatar_data[0]
        serializer = AvatarDataSerializer(avatar_data)
        general_data["avatar_design"] = serializer.data
        if avatar_data.show_tutorial:
            avatar_data.show_tutorial = False
            avatar_data.save()
    general_data["first_name"] = user.salttrackeruser.nickname		
    general_data["gender"] = user.salttrackeruser.sex
    general_data["date_of_birth"] = user.salttrackeruser.date_of_birth
    general_data["height"] = user.salttrackeruser.height
    general_data["weight"] = user.salttrackeruser.weight
    return general_data

def __map_nutrition_levels(nutrition_levels, gender, number_of_days_back):
    salt_level = __map_salt_level(nutrition_levels["total_salt__sum"]/number_of_days_back) # average salt, total comes from django/sql
    added_sugar_level = __map_sugar_level(nutrition_levels["total_added_sugar__sum"]/number_of_days_back)
    fruit_and_vegetable_level = __map_fruit_and_vegetable_level(nutrition_levels["total_fruit__sum"]/number_of_days_back + nutrition_levels["total_vegetables__sum"]/number_of_days_back)
    alcohol_level = __map_alcohol_level(nutrition_levels["total_alcohol__sum"]/number_of_days_back, gender)
    return salt_level, added_sugar_level, fruit_and_vegetable_level, alcohol_level

def __generate_message(nutrients_dict, best_nutrient, worst_nutrient):
    cursor = connection.cursor()
    nutrients = ["Overall", "Last Protocol", best_nutrient, worst_nutrient]
    sql = "Select message from avatar_message where ingredient_level = %s and ingredient= %s;"
    result_string = ""
    for nutrient in nutrients:
        level = int(round(float(nutrients_dict[nutrient])))
        cursor.execute(sql, [level, nutrient])
        row = cursor.fetchone()
        result_string = result_string + " " + row[0] 
    return result_string[1:]

def __generate_tips(nutrients_dict, best_nutrient, worst_nutrient):
    tips = AvatarTip.objects.filter(Q(ingredient_level=nutrients_dict[best_nutrient], ingredient = best_nutrient) | Q(ingredient_level=nutrients_dict[worst_nutrient], ingredient = worst_nutrient)).values("message")
    return tips

def __find_best_and_worst_level(nutrients_dict):
    best = 0
    best_nutrient = ""
    worst_nutrient = ""
    worst = 10
    for nutrient in nutrients_dict:
        if nutrient != "Overall" and nutrient != "Last Protocol":
            if nutrients_dict[nutrient] >= best:
                best_nutrient = nutrient
                best = nutrients_dict[nutrient]
            if nutrients_dict[nutrient] <= worst:
                worst_nutrient = nutrient
                worst = nutrients_dict[nutrient]
    return best_nutrient, worst_nutrient

def __map_visual_variable(primary_influencer, secondary_influencer, influence_primary):
    return influence_primary*primary_influencer + (1-influence_primary)*secondary_influencer


def __map_salt_level(salt_level):
    if salt_level < 5:
        return 1
    elif salt_level < 6:
        return 2
    elif salt_level < 8:
        return 3
    elif salt_level < 10:
        return 4
    else:
        return 5

def __map_sugar_level(sugar_level): # only maps added_sugar based on current method input
    if sugar_level < 25:
        return 1
    elif sugar_level < 50:
        return 2
    elif sugar_level < 70:
        return 3
    elif sugar_level < 85:
        return 4
    else:
        return 5


def __map_fruit_and_vegetable_level(fruit_level): #maps both fruit and vegetables based on current method input
    if fruit_level >= 600:
        return 1
    elif fruit_level >= 480:
        return 2
    elif fruit_level >= 240:
        return 3
    elif fruit_level >= 120:
        return 4
    else:
        return 5


def __map_alcohol_level(alcohol_level, gender):
	if gender == SaltTrackerUser.MALE: # if gender = male
		if alcohol_level <= 0:
			return 1
		elif alcohol_level <= 20:
			return 2
		elif alcohol_level <= 25:
			return 3
		elif alcohol_level <= 30:
			return 4
		else:
			return 5
	else: # else (gender = female), reduce limits by 10g
		if alcohol_level <= 0:
			return 1
		elif alcohol_level <= 10:
			return 2
		elif alcohol_level <= 15:
			return 3
		elif alcohol_level <= 20:
			return 4
		else:
			return 5	
		