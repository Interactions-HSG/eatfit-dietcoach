from django.db import connection
from TrustBoxAPI.models import Product, MissingTrustboxItem, NutritionFact, ImportLog
from SaltTrackerService.models import SaltTrackerUser, MigrosItem, MigrosBasketItem, ShoppingResult
from datetime import datetime
from django.db.models.aggregates import Sum

def calculate_shopping_results(user):
    count = 0.0
    cursor = connection.cursor()
    try:
        latest_entry = ShoppingResult.objects.using("salttracker").filter(user=user.user).latest("added")
        basket_items = MigrosBasketItem.objects.using("salttracker").filter(migros_basket__user=user, migros_basket__added_date__gt=latest_entry.added, migros_item__gtin__gt=0).values('migros_item__gtin','quantity', "migros_basket__date_of_purchase_millis")
    except:
        basket_items = MigrosBasketItem.objects.using("salttracker").filter(migros_basket__user=user, migros_item__gtin__gt=0).values('migros_item__gtin','quantity', "migros_basket__date_of_purchase_millis")
        
    number_of_items = basket_items.count()
    print(number_of_items)
    if number_of_items > 0:
        gtins = [x["migros_item__gtin"] for x in basket_items]
        gtin_string_list = ",".join(str(gtin) for gtin in gtins)
        sql = "SELECT p.gtin, fact.amount, fact.unit_of_measure, fact.canonical_name,g.value, category.description FROM nutrition_fact as fact, nutrition_group_attribute as g, product as p, nwd_subcategory as category where p.gtin IN (%s) and p.nwd_subcategory_id = category.id and  fact.nutrition_facts_group_id = p.id and fact.nutrition_facts_group_id = g.nutrition_facts_group_id and g.canonical_name = 'servingSize' and fact.canonical_name = 'salt' and amount is not null and ISNUMERIC(amount)= 1 and amount <> '-' and amount <> '0' and (g.language_code='de' or g.language_code is null)" % gtin_string_list
        nutritions = cursor.execute(sql)
        rows = cursor.fetchall()
        missing_items_dict = {}
        products_dict = {}
        missing_items = MissingTrustboxItem.objects.filter(gtin__in=gtins)
        for missing_item in missing_items:
            missing_items_dict[missing_item.gtin] = missing_item
        for row in rows:
            products_dict[row[0]] = row
        for basket_item in basket_items:
            basket_item_gtin = basket_item["migros_item__gtin"]
            if basket_item_gtin in missing_items_dict:
                count = count +1 
                basket_item["total_salt"] = missing_items_dict[basket_item_gtin].total_weight * (missing_items_dict[basket_item_gtin].salt * 0.1) * basket_item["quantity"]
                if missing_items_dict[basket_item_gtin].nwd_subcategory:
                    basket_item["category"] = missing_items_dict[basket_item_gtin].nwd_subcategory
            elif basket_item_gtin in products_dict:
                if is_number(row[1]) and is_number(row[4]):
                    basket_item["total_salt"] = (float(row[1]) * 0.1) * float(row[4]) * basket_item["quantity"]
                    basket_item["category"] = row[5]
                    count = count + 1
        percent = (count/len(basket_items))*100
        print(str(percent) + " %")
        save_count = 0
        for basket_item in basket_items:
            if "total_salt" in basket_item:
                if "category" in basket_item:
                    ShoppingResult.objects.using("salttracker").create(gtin = basket_item["migros_item__gtin"], purchased= datetime.fromtimestamp(basket_item["migros_basket__date_of_purchase_millis"]/1000.0), total_salt = basket_item["total_salt"], quantity = basket_item["quantity"], user = user.user, nwd_subcategory_name = basket_item["category"], added = datetime.now())
                else:
                    ShoppingResult.objects.using("salttracker").create(gtin = basket_item["migros_item__gtin"], purchased= datetime.fromtimestamp(basket_item["migros_basket__date_of_purchase_millis"]/1000.0), total_salt = basket_item["total_salt"], quantity = basket_item["quantity"], user = user.user, added = datetime.now())
                save_count = save_count + 1
                print("saved item: " + str(save_count))
        ImportLog.objects.create(import_timestamp = datetime.now(), successful=True, failed_reason = "Added shopping results")


def get_shopping_tips(user_pk):
    cursor = connection.cursor()
    shopping_results = ShoppingResult.objects.using("salttracker").filter(user_id=user_pk).values("nwd_subcategory_name").annotate(total_salt = Sum("total_salt")).order_by("-total_salt")[:5]
    result_dict = []
    for shopping_result in shopping_results:
        sql = "SELECT p.id, p.gtin, fact.amount, att.value FROM nutrition_fact as fact, product as p,  nwd_subcategory as category, nutrition_group_attribute as att where p.nwd_subcategory_id = category.id and category.description = %s and fact.nutrition_facts_group_id = p.id and fact.canonical_name = 'salt' and fact.amount <> '0' and att.nutrition_facts_group_id = p.id and att.canonical_name = 'servingSize' and (att.language_code = 'de' or att.language_code is null) order by fact.amount;"
        cursor.execute(sql, [shopping_result["nwd_subcategory_name"]])
        rows = cursor.fetchall()
        for row in rows:
            if len(row) > 0:
                sql = "SELECT names.name, att.value FROM product as p, product_attribute as att, product_name as names where p.id = %s and att.product_id = p.id and att.canonical_name = 'productImageURL' and (att.language_code = 'de' or att.language_code is null) and names.product_id = p.id and (names.language_code = 'de' or names.language_code is null);" % row[0]
                cursor.execute(sql)
                result = cursor.fetchone()
                if len(result) > 0:
                    result_dict.append({"name" : result[0], "image" : result[1], "gtin" : row[1], "category" : shopping_result["nwd_subcategory_name"]})
                    break
    return result_dict



def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False