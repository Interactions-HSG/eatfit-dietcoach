from django.shortcuts import render
from django.http.response import HttpResponse
from SaltTrackerService.models import SaltTrackerUser, MigrosItem, MigrosBasketItem
from SaltTrackerService import reebate_connector
from django.contrib.auth.decorators import login_required
from TrustBoxAPI.models import Product, MissingTrustboxItem, NutritionFact
from django.db import connection
import datetime

@login_required
def test(request):
    reebate_connector.fill_db()
    return HttpResponse("")


def get_shopping_results(request, user_pk):
    count = 0.0
    cursor = connection.cursor()
    basket_items = MigrosBasketItem.objects.using("salttracker").filter(migros_basket__user__pk=user_pk, migros_item__gtin__gt=0).values('migros_item__gtin','quantity', "migros_basket__date_of_purchase_millis")
    gtins = [x["migros_item__gtin"] for x in basket_items]
    gtin_string_list = ",".join(str(gtin) for gtin in gtins)
    sql = "SELECT p.gtin, fact.amount, fact.unit_of_measure, fact.canonical_name,g.value, p.nwd_subcategory_id FROM nutrition_fact as fact, nutrition_group_attribute as g, product as p where p.gtin IN (%s) and fact.nutrition_facts_group_id = p.id and fact.nutrition_facts_group_id = g.nutrition_facts_group_id and g.canonical_name = 'servingSize' and fact.canonical_name = 'salt' and amount is not null and ISNUMERIC(amount)= 1 and amount <> '-' and amount <> '0' and (g.language_code='de' or g.language_code is null)" % gtin_string_list
    nutritions = cursor.execute(sql)
    rows = cursor.fetchall()
    missing_items_dict = {}
    products_dict = {}
    print("Here0")
    missing_items = MissingTrustboxItem.objects.filter(gtin__in=gtins)
    for missing_item in missing_items:
        missing_items_dict[missing_item.gtin] = missing_item
    for row in rows:
        products_dict[row[0]] = row
    print("Here1")
    for basket_item in basket_items:
        basket_item_gtin = basket_item["migros_item__gtin"]
        print("Here3")
        if basket_item_gtin in missing_items_dict:
            count = count +1 
            basket_item["total_salt"] = missing_items_dict[basket_item_gtin].total_weight * (missing_items_dict[basket_item_gtin].salt * 0.1) * basket_item["quantity"]
            if missing_items_dict[basket_item_gtin].nwd_subcategory:
                basket_item["category"] = missing_items_dict[basket_item_gtin].nwd_subcategory.pk
        elif basket_item_gtin in products_dict:
            if is_number(row[1]) and is_number(row[4]):
                basket_item["total_salt"] = (float(row[1]) * 0.1) * float(row[4]) * basket_item["quantity"]
                basket_item["category"] = row[5]
                count = count + 1
    percent = (count/len(basket_items))*100
    print(str(percent) + " %")
    for basket_item in basket_items:
        pass
        #ShoppingResult.objects.create(gtin = basket_item["migros_item__gtin"], purchased=date = datetime.datetime.fromtimestamp(basket_item["migros_basket__date_of_purchase_millis"]/1000.0), total_salt = basket_item["total_salt"], quantity = basket_item["quantity"], user = user_pk, nwd_subcategory = basket_item["category"], added = datetime.datetime.now())
    return HttpResponse("")


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False