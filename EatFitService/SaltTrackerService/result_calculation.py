from django.db import connection
from TrustBoxAPI.models import Product, MissingTrustboxItem, NutritionFact, ImportLog
from SaltTrackerService.models import SaltTrackerUser, MigrosItem, MigrosBasketItem, ShoppingResult
from datetime import datetime
from django.db.models.aggregates import Sum, Avg
from django.db.models import F

def calculate_shopping_results(user):
    count = 0.0
    cursor = connection.cursor()
    basket_items = __get_basket_items(user)
    number_of_items = basket_items.count()
    print(number_of_items)
    if number_of_items > 0:
        gtins = [x["migros_item__gtin"] for x in basket_items]
        gtin_string_list = ",".join(str(gtin) for gtin in gtins)
        sql = "SELECT p.gtin, fact.amount, fact.unit_of_measure, fact.canonical_name,g.value,category.description, fact2.amount as fat, fact3.amount as sugar FROM nutrition_fact as fact,nutrition_fact as fact2,nutrition_fact as fact3, nutrition_group_attribute as g, product as p, nwd_subcategory as category where p.gtin IN (%s) and p.nwd_subcategory_id = category.id and  fact.nutrition_facts_group_id = p.id and fact2.nutrition_facts_group_id = p.id and fact3.nutrition_facts_group_id = p.id and fact.nutrition_facts_group_id = g.nutrition_facts_group_id and g.canonical_name = 'servingSize' and fact.canonical_name = 'salt' and fact2.canonical_name='totalFat' and fact3.canonical_name ='sugars' and fact.amount is not null and ISNUMERIC(fact.amount)= 1 and fact.amount <> '-' and fact.amount <> '0' and (g.language_code='de' or g.language_code is null)" % gtin_string_list
        nutritions = cursor.execute(sql)
        rows = cursor.fetchall()
        missing_items_dict = {}
        products_dict = {}
        missing_items_sql = "Select * from missing_trustbox_item where gtin in (%s)" % gtin_string_list
        missing_items = MissingTrustboxItem.objects.raw(missing_items_sql)
        for missing_item in missing_items:
            missing_items_dict[missing_item.gtin] = missing_item
        for row in rows:
            products_dict[row[0]] = row
        for basket_item in basket_items:
            basket_item_gtin = basket_item["migros_item__gtin"]
            if basket_item_gtin in missing_items_dict:
                __get_items_from_missing_trustbox_items(basket_item, missing_items_dict, basket_item_gtin)
                count = count +1 
            elif basket_item_gtin in products_dict:
                __get_items_from_trustbox(basket_item, products_dict, basket_item_gtin)
                count = count + 1
        percent = (count/len(basket_items))*100
        print(str(percent) + " %")
        save_count = 0
        for basket_item in basket_items:
            if "total_salt" in basket_item:
                __create_shopping_result(basket_item, user.user)
                save_count = save_count + 1
                print("saved item: " + str(save_count))
        ImportLog.objects.create(import_timestamp = datetime.now(), successful=True, failed_reason = "Added shopping results")


def get_shopping_tips(user_pk):
    cursor = connection.cursor()
    shopping_results = ShoppingResult.objects.using("salttracker").filter(user_id=user_pk).values("nwd_subcategory_name").annotate(total_salt = Sum("total_salt")).order_by("-total_salt")[:5]
    result_dict = []
    for shopping_result in shopping_results:
        fat_results = ShoppingResult.objects.using("salttracker").filter(nwd_subcategory_name=shopping_result["nwd_subcategory_name"], total_fat__gt= 0, serving_size__gt=0).aggregate(average_fat = Avg((F("total_fat")/F("quantity"))))
        sugar_results = ShoppingResult.objects.using("salttracker").filter(nwd_subcategory_name=shopping_result["nwd_subcategory_name"], total_sugar__gt= 0, serving_size__gt=0).aggregate(average_sugar = Avg((F("total_sugar")/F("quantity"))))
        sql = "SELECT p.id, p.gtin, fact.amount, att.value, fact2.amount as fat, fact3.amount as sugar FROM nutrition_fact as fact, nutrition_fact as fact2,nutrition_fact as fact3, product as p,  nwd_subcategory as category, nutrition_group_attribute as att where p.nwd_subcategory_id = category.id and category.description = %s and fact.nutrition_facts_group_id = p.id and fact2.nutrition_facts_group_id = p.id and fact3.nutrition_facts_group_id = p.id and fact.canonical_name = 'salt' and fact2.canonical_name='totalFat' and fact3.canonical_name='sugars' and fact.amount <> '0' and att.nutrition_facts_group_id = p.id and att.canonical_name = 'servingSize' and (att.language_code = 'de' or att.language_code is null) order by fact.amount;"
        cursor.execute(sql, [shopping_result["nwd_subcategory_name"]])
        rows = cursor.fetchall()
        for row in rows:
            if len(row) > 0:
                if is_number(row[3]) and is_number(row[4]) and is_number(row[5]):
                    if (float(row[3]) * float(row[4])*0.01) < 1.2*fat_results["average_fat"] and (float(row[3]) * float(row[5])*0.01) < 1.2*sugar_results["average_sugar"]:
                        sql = "SELECT names.name, att.value FROM product as p, product_attribute as att, product_name as names where p.id = %s and att.product_id = p.id and att.canonical_name = 'productImageURL' and (att.language_code = 'de' or att.language_code is null) and names.product_id = p.id and (names.language_code = 'de' or names.language_code is null);" % row[0]
                        cursor.execute(sql)
                        result = cursor.fetchone()
                        if len(result) > 0:
                            result_dict.append({"name" : result[0], "image" : result[1], "gtin" : row[1], "category" : shopping_result["nwd_subcategory_name"]})
                            break
    return result_dict


def __get_items_from_missing_trustbox_items(basket_item,missing_items_dict,basket_item_gtin):
    basket_item["total_salt"] = missing_items_dict[basket_item_gtin].serving_size * (missing_items_dict[basket_item_gtin].salt * 0.01) * basket_item["quantity"]
    basket_item["fat"] = missing_items_dict[basket_item_gtin].serving_size * (missing_items_dict[basket_item_gtin].fat * 0.01) * basket_item["quantity"]
    basket_item["sugar"] = missing_items_dict[basket_item_gtin].serving_size * (missing_items_dict[basket_item_gtin].sugar * 0.01) * basket_item["quantity"]
    basket_item["serving_size"] = missing_items_dict[basket_item_gtin].serving_size
    if missing_items_dict[basket_item_gtin].nwd_subcategory:
        basket_item["category"] = missing_items_dict[basket_item_gtin].nwd_subcategory.description

def __get_items_from_trustbox(basket_item,products_dict,basket_item_gtin):
    row = products_dict[basket_item_gtin]
    if is_number(row[1]) and is_number(row[4]):
        basket_item["total_salt"] = (float(row[1]) * 0.01) * float(row[4]) * basket_item["quantity"]
        if is_number(row[6]):
            basket_item["fat"] = (float(row[6]) * 0.01) * float(row[4]) * basket_item["quantity"]
        if is_number(row[7]):
            basket_item["sugar"] = (float(row[7]) * 0.01) * float(row[4]) * basket_item["quantity"]
        basket_item["category"] = row[5]
        basket_item["serving_size"] = row[4]

def __create_shopping_result(basket_item, user):
    create_arguments = {}
    create_arguments["gtin"] = basket_item["migros_item__gtin"]
    create_arguments["purchased"] = datetime.fromtimestamp(basket_item["migros_basket__date_of_purchase_millis"]/1000.0)
    create_arguments["total_salt"] = basket_item["total_salt"]
    create_arguments["quantity"] = basket_item["quantity"]
    create_arguments["added"] = datetime.now()
    create_arguments["user"] = user
    create_arguments["total_fat"] = 0
    create_arguments["total_sugar"] = 0
    create_arguments["serving_size"] = 0
    if "fat" in basket_item:
        create_arguments["total_fat"] = basket_item["fat"]
    if "sugar" in basket_item:
        create_arguments["total_sugar"] = basket_item["sugar"]
    if "serving_size" in basket_item:
        create_arguments["serving_size"] = basket_item["serving_size"]
    if "category" in basket_item:
        create_arguments["nwd_subcategory_name"] = basket_item["category"]
    ShoppingResult.objects.using("salttracker").create(**create_arguments)

def __get_basket_items(user):
    basket_items = []
    try:
        latest_entry = ShoppingResult.objects.using("salttracker").filter(user=user.user).latest("added")
        basket_items = MigrosBasketItem.objects.using("salttracker").filter(migros_basket__user=user, migros_basket__added_date__gt=latest_entry.added, migros_item__gtin__gt=0).values('migros_item__gtin','quantity', "migros_basket__date_of_purchase_millis")
    except:
        basket_items = MigrosBasketItem.objects.using("salttracker").filter(migros_basket__user=user, migros_item__gtin__gt=0).values('migros_item__gtin','quantity', "migros_basket__date_of_purchase_millis")
    return basket_items

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False