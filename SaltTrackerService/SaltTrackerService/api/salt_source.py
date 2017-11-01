
from api.models import ProfileData, FoodRecord
from api import results
from django.db.models.aggregates import Sum
from django.db import connections


def salt_from_checklist(users):
    result_dict = {}
    cat_dict = {}
    number_of_users = 0.0
    for user in users: 
        number_of_users = number_of_users + 1
        user_dict = {}
        records = FoodRecord.objects.filter(user=user.user, study_day__is_locked=True).select_related("food_item", "food_item__category")
        sum_user = 0.0
        for record in records:
            sum_user = sum_user + record.total_salt
            if record.food_item.category.name in user_dict:
                user_dict[record.food_item.category.name] = user_dict[record.food_item.category.name] + record.total_salt
            else:
                user_dict[record.food_item.category.name] = record.total_salt
        result_dict[user.pk] = {}
        for cat in user_dict:
            result_dict[user.pk][cat] = {}
            result_dict[user.pk][cat] = user_dict[cat] / sum_user
    for k in result_dict:
        print("User with id: " + str(k))
        for cat in result_dict[k]:
            if cat in cat_dict:
                cat_dict[cat] = cat_dict[cat] + result_dict[k][cat]*100
            else:
                cat_dict[cat] = result_dict[k][cat]*100
            #print(cat + ";" + str(result_dict[k][cat]*100))
    for cat in cat_dict:
        print(cat + ";" + str(cat_dict[cat]/number_of_users))


def mapping_results(user):
    cursor = connections["default"].cursor()
    cursor_eatfit = connections['eatfit'].cursor()
    cursor.execute("SELECT distinct(item.name), gtin FROM [dbo].[autoid_scraper_migros_basket_item] as basket_item, autoid_scraper_migros_basket as basket, autoid_scraper_migros_item as item where basket_item.autoid_scraper_migros_item_id = item.id and basket.id = autoid_scraper_migros_basket_id and basket.user_id=%s", [user.user.pk])
    rows = cursor.fetchall()
    cursor.execute("SELECT gtin, count(*) FROM [dbo].[autoid_scraper_migros_basket_item] as basket_item, autoid_scraper_migros_basket as basket, autoid_scraper_migros_item as item where basket_item.autoid_scraper_migros_item_id = item.id and basket.id = autoid_scraper_migros_basket_id and basket.user_id=%s and item.gtin is not null group by gtin", [user.user.pk])
    total_rows = cursor.fetchall()
    products_matched_total = 0
    for r in total_rows:
        products_matched_total = products_matched_total + r[1]
    gtins = [x[1] for x in rows if x[1] and int(x[1]) > 0]
    irrelevant_gtins = [x[1] for x in rows if x[1] and int(x[1]) == -1]
    gtin_string_list = ",".join(str(gtin) for gtin in gtins)
    ratio = 0
    trustbox_row_count = 0.0
    missing_row_count = 0.0
    product_dict = {}
    duplicates = 0
    if len(rows) > 0:
        ratio = (len(gtins)/float((len(rows) - len(irrelevant_gtins))))*100
        sql = "SELECT p.gtin, category.description, a1.value, a2.value FROM product as p, nwd_subcategory as category, product_attribute as a1, product_attribute as a2 where p.gtin IN (%s) and p.nwd_subcategory_id = category.id and a1.product_id = p.id and a1.canonical_name='packageSize' and isnumeric(a1.value) = 1 and a2.product_id = p.id and a2.canonical_name='packageSize_uom' and (a1.language_code = 'de' or a1.language_code is null) and (a2.language_code = 'de' or a2.language_code is null)" % gtin_string_list
        cursor_eatfit.execute(sql)
        trustbox_rows = cursor_eatfit.fetchall()
        for row in trustbox_rows:
            product_dict[row[0]] = 1
            trustbox_row_count = trustbox_row_count + 1

        # get the products and categories from the manually added items
        missing_items_sql = "Select item.gtin, main.description from missing_trustbox_item as item, nwd_subcategory as sub, nwd_main_category as main where gtin in (%s) and item.nwd_subcategory_id is not null and item.nwd_subcategory_id = sub.id and sub.nwd_main_category_id = main.nwd_main_category_id" % gtin_string_list
        cursor_eatfit.execute(missing_items_sql)
        missing_rows = cursor_eatfit.fetchall()
        for row in missing_rows:
            if row[0] in product_dict:
                duplicates = duplicates + 1
            product_dict[row[0]] = 1
            missing_row_count = missing_row_count + 1 
        print("*********************************************")
        print("User: " + str(user.user.pk))
        print("Total number of items matched: " + str(products_matched_total))
        print("unqiue purchased items: " + str(len(rows)))
        print("Mapped Items: " + str(len(gtins)))
        print("Found: " + str(len(product_dict)))
        print("Irrelevant items: " + str(len(irrelevant_gtins)))
        print("Mapped items: " + str(ratio) + "%")
        print("Items from Trustbox: " + str(trustbox_row_count/len(gtins)))
        print("Items from MissingItemsTable: " + str(missing_row_count/len(gtins)))
        print("Items in both: " + str(duplicates))
        print("*********************************************")

def salt_from_purchase_data(user):
    real_salt_intake = results.get_average_salt_per_day(user.user)
    total_cumulus_salt_intake = 0
    shopping_results = results.get_shopping_results(user.user)
    number_of_baskets = len(shopping_results)
    for s_result in shopping_results:
        total_cumulus_salt_intake = total_cumulus_salt_intake + s_result["total_salt"]
    if number_of_baskets > 0:
        cumulus_salt_intake = total_cumulus_salt_intake/number_of_baskets
        profile_data = ProfileData.objects.filter(user=user.user)
        number_of_adult_housemates = int(filter(str.isdigit, str(profile_data.filter(name = "NumberOfAdultHousemates").values_list("value", flat=True)[0])))
        number_of_child_housemates = int(filter(str.isdigit, str(profile_data.filter(name = "NumberOfChildHousemates").values_list("value", flat=True)[0])))
        migros_purchase_share = profile_data.filter(name = "MigrosShare").values_list("value", flat=True)[0]
        migros_cumulus_usage = profile_data.filter(name = "CumulusUsage").values_list("value", flat=True)[0]

        household_divisor = (number_of_adult_housemates + number_of_child_housemates/2)
        highest_salt_intake = real_salt_intake
        lowest_salt_intake = real_salt_intake
        cumulus_salt_intake = cumulus_salt_intake / household_divisor

        if migros_purchase_share == "0-20%":
            highest_salt_intake = highest_salt_intake * 0.2
            lowest_salt_intake = lowest_salt_intake * 0
        elif migros_purchase_share == "20-40%":
            highest_salt_intake = highest_salt_intake * 0.4
            lowest_salt_intake = lowest_salt_intake * 0.2
        elif migros_purchase_share == "40-60%":
            highest_salt_intake = highest_salt_intake * 0.6
            lowest_salt_intake = lowest_salt_intake * 0.4
        elif migros_purchase_share == "60-80%":
            highest_salt_intake = highest_salt_intake * 0.8
            lowest_salt_intake = lowest_salt_intake * 0.6
        elif migros_purchase_share == "80-100%":
            highest_salt_intake = highest_salt_intake
            lowest_salt_intake = lowest_salt_intake * 0.8
    
        if migros_cumulus_usage == "0-20%":
            highest_salt_intake = highest_salt_intake * 0.2
            lowest_salt_intake = lowest_salt_intake * 0
        elif migros_cumulus_usage == "20-40%":
            highest_salt_intake = highest_salt_intake * 0.4
            lowest_salt_intake = lowest_salt_intake * 0.2
        elif migros_cumulus_usage == "40-60%":
            highest_salt_intake = highest_salt_intake * 0.6
            lowest_salt_intake = lowest_salt_intake * 0.4
        elif migros_cumulus_usage == "60-80%":
            highest_salt_intake = highest_salt_intake * 0.8
            lowest_salt_intake = lowest_salt_intake * 0.6
        elif migros_cumulus_usage == "80-100%":
            highest_salt_intake = highest_salt_intake
            lowest_salt_intake = lowest_salt_intake * 0.8
        print("*********************************************")
        print("User: " + str(user.user.pk))
        print("real salt intake:" + str(real_salt_intake))
        print("Cumulus salt intake:" + str(cumulus_salt_intake))
        print("lowest calculated salt intake:" + str(lowest_salt_intake))
        print("highest calculated salt intake:" + str(highest_salt_intake))
        print("*********************************************")
