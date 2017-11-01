
from api.models import FoodRecord, MigrosBasket, MigrosBasketItem, ShoppingResult
from django.db.models.aggregates import Count
from django.db.models import F, Sum
from api.eatfit_models import NwdSubcategory


def get_average_salt_per_day(user, last_n_days=0):
    if last_n_days > 0:
        records = FoodRecord.objects.filter(user=user, study_day__is_locked=True).values("date").order_by("-date").annotate(Sum("total_salt"))[:7]
    else:
        records = FoodRecord.objects.filter(user=user, study_day__is_locked=True).values("date").order_by("-date").annotate(Sum("total_salt"))
    records_count = records.count()
    average_salt = 0
    total_salt = 0
    records_count = 0
    for record in records:
        records_count = records_count + 1
        total_salt = total_salt + record["total_salt__sum"]
    if records_count > 0:
        average_salt = total_salt/records_count
    return average_salt

def get_average_salt_per_day_for_study(user):
    records = FoodRecord.objects.filter(user=user, study_day__is_locked=True).values("date").order_by("date").annotate(Sum("total_salt"))[1:4]
    records_count = records.count()
    average_salt = 0
    total_salt = 0
    records_count = 0
    for record in records:
        records_count = records_count + 1
        total_salt = total_salt + record["total_salt__sum"]
    if records_count > 0:
        average_salt = total_salt/records_count
    return average_salt


def get_food_record_result(user):
    food_records = FoodRecord.objects.filter(user=user, study_day__is_locked=True).values("date").annotate(total_salt = Sum("total_salt"))
    return food_records


def get_food_record_worst_categories(user):
    return FoodRecord.objects.filter(user=user, study_day__is_locked=True).values("food_item__category").annotate(total_salt = Sum("total_salt")).order_by("-total_salt")[:5]

def get_total_salt_daytimes(user):
     return FoodRecord.objects.filter(user=user, study_day__is_locked=True).values("daytime").annotate(total_salt = Sum("total_salt")).order_by("-total_salt")[:5]


def get_shopping_results(user):
    shopping_results = ShoppingResult.objects.filter(user=user).values("purchased").annotate(total_salt = Sum("total_salt"))
    return shopping_results

def get_shopping_worst_categories(user):
    shopping_results = ShoppingResult.objects.filter(user=user).values("nwd_subcategory_name").annotate(total_salt = Sum("total_salt")).order_by("-total_salt")[:5]
    category_names = [x["nwd_subcategory_name"] for x in shopping_results]
    categories = NwdSubcategory.objects.using("eatfit").filter(description__in = category_names).values("description", "icon")
    category_dict = {}
    for cat in categories:
        category_dict[cat["description"]] = cat["icon"]
    try:
        for shopping_result in shopping_results:
            shopping_result["icon"] = category_dict[shopping_result["nwd_subcategory_name"]]
    except:
        pass
    return shopping_results
