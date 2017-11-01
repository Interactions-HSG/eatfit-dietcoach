#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
from api.models import AutoidScraperMigrosBasketItem, ProfileData
from api.eatfit_models import MissingTrustboxItem, NwdMainCategory, NwdSubcategory
from django.db.models.aggregates import Sum
from django.db import connections
from api import results
from datetime import datetime

MULTIPLY_NUMBER = 10000

"""Setup"""

def _add_one_time_questions(user, result_list):
    profile_data = ProfileData.objects.filter(user=user)
    number_of_adult_housemates = int(filter(str.isdigit, str(profile_data.filter(name = "NumberOfAdultHousemates").values_list("value", flat=True)[0])))
    #number_of_child_housemates = int(filter(str.isdigit, str(profile_data.filter(name = "NumberOfChildHousemates").values_list("value", flat=True)[0])))
    migros_purchase_share = profile_data.filter(name = "MigrosShare").values_list("value", flat=True)[0]
    migros_cumulus_usage = profile_data.filter(name = "CumulusUsage").values_list("value", flat=True)[0]
    eat_outwards_breakfast = int(profile_data.filter(name = "EatOutwardsBreakfast").values_list("value", flat=True)[0])
    eat_outwards_lunch = int(profile_data.filter(name = "EatOutwardsLunch").values_list("value", flat=True)[0])
    eat_outwards_dinner = int(profile_data.filter(name = "EatOutwardsDinner").values_list("value", flat=True)[0])
    gender = user.salttrackeruser.sex
    result_list[1] = number_of_adult_housemates
    result_list[2] = migros_purchase_share
    result_list[3] = migros_cumulus_usage
    result_list[4] = (eat_outwards_breakfast + eat_outwards_lunch + eat_outwards_dinner)
    result_list[5] = gender
    result_list[6] = datetime.now().date().year - user.salttrackeruser.date_of_birth.year
    result_list[7] = user.salttrackeruser.weight

def __custom_category_setup(response):
    cursor = connections['eatfit'].cursor()
    cvs_data = []
    header = []
    relative_spending = {}
    header.append("UserId")
    header.append("Household Size")
    header.append("Migros Share")
    header.append("Cumulus Usage")
    header.append("Outdoor eating")
    header.append("Gender")
    header.append("Age")
    header.append("Weight")
    
    header.append(u"Brote")
    relative_spending[u"Brote"] = 0.0
    header.append(u"Flocken und Cerealien")
    relative_spending[u"Flocken und Cerealien"] = 0.0
    header.append(u"Fette und Öle")
    relative_spending[u"Fette und Öle"] = 0.0
    header.append(u"Wuerste")
    relative_spending[u"Wuerste"] = 0.0
    header.append(u"Fleich")
    relative_spending[u"Fleich"] = 0.0
    header.append(u"Früchte")
    relative_spending[u"Früchte"] = 0.0
    header.append(u"Gemüse")
    relative_spending[u"Gemüse"] = 0.0
    header.append(u"Gerichte")
    relative_spending[u"Gerichte"] = 0.0
    header.append(u"Salzige Snacks")
    relative_spending[u"Salzige Snacks"] = 0.0
    header.append(u"Kaese")
    relative_spending[u"Kaese"] = 0.0
    header.append(u"Milch")
    relative_spending[u"Milch"] = 0.0
    header.append(u"Nüsse, Samen und Ölfrüchte")
    relative_spending[u"Nüsse, Samen und Ölfrüchte"] = 0.0
    header.append(u"Süssigkeiten")
    relative_spending[u"Süssigkeiten"] = 0.0
    header.append(u"Getreideprodukte, Hülsenfrüchte und Kartoffeln")
    relative_spending[u"Getreideprodukte, Hülsenfrüchte und Kartoffeln"] = 0.0
    header.append(u"Verschiedenes")
    relative_spending[u"Verschiedenes"] = 0.0
    header.append(u"Alkoholfreie Getränke")
    relative_spending[u"Alkoholfreie Getränke"] = 0.0
    header.append(u"Fisch")
    relative_spending[u"Fisch"] = 0.0

    header.append("Dependent Variable")
    writer = csv.writer(response, delimiter=";")
    writer.writerow([x.encode("utf-8") for x in header])
    return cursor, cvs_data, header, relative_spending, writer, response

def __main_category_setup(response):
    cursor = connections['eatfit'].cursor()
    cvs_data = []
    header = []
    relative_spending = {}
    header.append("UserId")
    header.append("Household Size")
    header.append("Migros Share")
    header.append("Cumulus Usage")
    header.append("Outdoor eating")
    header.append("Gender")
    header.append("Age")
    header.append("Weight")
    for main_category in NwdMainCategory.objects.using("eatfit").all():
        header.append(main_category.description)
        relative_spending[main_category.description] = 0.0
    header.append("Dependent Variable")
    writer = csv.writer(response, delimiter=";")
    writer.writerow([x.encode("utf8") for x in header])
    return cursor, cvs_data, header, relative_spending, writer, response

def __minor_category_setup(response):
    cursor = connections['eatfit'].cursor()
    cvs_data = []
    header = []
    relative_spending = {}
    header.append("UserId")
    header.append("Household Size")
    header.append("Migros Share")
    header.append("Cumulus Usage")
    header.append("Outdoor eating")
    header.append("Gender")
    header.append("Age")
    header.append("Weight")
    for sub_category in NwdSubcategory.objects.using("eatfit").all():
        header.append(sub_category.description)
        relative_spending[sub_category.description] = 0.0
    header.append("Dependent Variable")
    writer = csv.writer(response, delimiter=";")
    writer.writerow([x.encode("utf8") for x in header])
    return cursor, cvs_data, header, relative_spending, writer, response

def __get_volume_of_sales(user):
    return AutoidScraperMigrosBasketItem.objects.filter(autoid_scraper_migros_basket__user__pk=user.pk, autoid_scraper_migros_item__gtin__gt=0).aggregate(Sum("price"))

def __get_purchased_products(user):
    basket_items = AutoidScraperMigrosBasketItem.objects.filter(autoid_scraper_migros_basket__user=user, autoid_scraper_migros_item__gtin__gt=0).values('autoid_scraper_migros_item__gtin','quantity', "price")
    gtins = [x["autoid_scraper_migros_item__gtin"] for x in basket_items]
    gtin_string_list = ",".join(str(gtin) for gtin in gtins)
    return basket_items, gtin_string_list

""" Product dicts """

def __generate_product_dict(missing_rows, rows, count):
    # put everything into a dictionary for faster lookup
    product_dict = {}
    for row in missing_rows:
        product_dict[row[0]] = row[1]
    for row in rows:
        product_dict[row[0]] = row[1]
    print("filled product dict for user: " + str(count))
    return product_dict

def __generate_product_dict_custom_cats(missing_rows, rows, count):
    # put everything into a dictionary for faster lookup
    product_dict = {}
    for row in missing_rows:
        product_dict[row[0]] = {"category": row[1], "sub_cat" : row[2]}
    for row in rows:
        product_dict[row[0]] = {"category": row[1], "sub_cat" : row[2]}
    print("filled product dict for user: " + str(count))
    return product_dict

def __generate_product_dict_weights(missing_rows, rows, count):
    # put everything into a dictionary for faster lookup
    product_dict = {}
    for row in missing_rows:
        product_dict[row[0]] = {"category" : row[1], "weight" : row[2]}
    for row in rows:
        weight = 0.0
        if row[3] == "kg" or row[3] == "l":
            weight = float(row[2])*1000
        elif row[3] == "g" or row[3] == "g":
            weight = float(row[2])
        elif row[3] == "mg" or row[3] == "ml":
            weight = float(row[2])*0.001
        if weight > 0:
            product_dict[row[0]] = {"category" : row[1], "weight" : weight}
    print("filled product dict for user: " + str(count))
    return product_dict

def __generate_product_dict_weights_custom_cats(missing_rows, rows, count):
    # put everything into a dictionary for faster lookup
    product_dict = {}
    for row in missing_rows:
        product_dict[row[0]] = {"category" : row[1], "weight" : row[2], "sub_cat" : row[3]}
    for row in rows:
        weight = 0.0
        if row[3] == "kg" or row[3] == "l":
            weight = float(row[2])*1000
        elif row[3] == "g" or row[3] == "g":
            weight = float(row[2])
        elif row[3] == "mg" or row[3] == "ml":
            weight = float(row[2])*0.001
        if weight > 0:
            product_dict[row[0]] = {"category" : row[1], "weight" : weight, "sub_cat" : row[4]}
    print("filled product dict for user: " + str(count))
    return product_dict

def __generate_product_dict_weights_and_salt(missing_rows, rows, count):
    # put everything into a dictionary for faster lookup
    product_dict = {}
    for row in missing_rows:
        product_dict[row[0]] = {"category" : row[1], "weight" : row[2], "salt" : row[3]}
    for row in rows:
        weight = 0.0
        if row[3] == "kg" or row[3] == "l":
            weight = float(row[2])*1000
        elif row[3] == "g" or row[3] == "g":
            weight = float(row[2])
        elif row[3] == "mg" or row[3] == "ml":
            weight = float(row[2])*0.001
        if weight > 0 and is_number(row[4]):
            product_dict[row[0]] = {"category" : row[1], "weight" : weight, "salt" : float(row[4])/100.0}
    print("filled product dict for user: " + str(count))
    return product_dict

def __generate_product_dict_weights_and_salt_custom_cat(missing_rows, rows, count):
    # put everything into a dictionary for faster lookup
    product_dict = {}
    for row in missing_rows:
        product_dict[row[0]] = {"category" : row[1], "weight" : row[2], "salt" : row[3], "sub_cat" : row[4]}
    for row in rows:
        weight = 0.0
        if row[3] == "kg" or row[3] == "l":
            weight = float(row[2])*1000
        elif row[3] == "g" or row[3] == "g":
            weight = float(row[2])
        elif row[3] == "mg" or row[3] == "ml":
            weight = float(row[2])*0.001
        if weight > 0 and is_number(row[4]):
            product_dict[row[0]] = {"category" : row[1], "weight" : weight, "salt" : float(row[4])/100.0, "sub_cat" : row[5]}
    print("filled product dict for user: " + str(count))
    return product_dict

""" Get products """

def __get_products_main_category(cursor, gtin_string_list, count):
    # get the products and categories from the Trustbox
    sql = "SELECT p.gtin, category.description FROM product as p, nwd_main_category as category where p.gtin IN (%s) and p.nwd_main_category_id = category.nwd_main_category_id" % gtin_string_list
    cursor.execute(sql)
    rows = cursor.fetchall()
    print("got Trustbox items for user: " + str(count))

    # get the products and categories from the manually added items
    missing_items_sql = "Select item.gtin, main.description from missing_trustbox_item as item, nwd_subcategory as sub, nwd_main_category as main where gtin in (%s) and item.nwd_subcategory_id is not null and item.nwd_subcategory_id = sub.id and sub.nwd_main_category_id = main.nwd_main_category_id" % gtin_string_list
    cursor.execute(missing_items_sql)
    missing_rows = cursor.fetchall()
    print("got missing items for user: " + str(count))

    return __generate_product_dict(missing_rows, rows, count)

def __get_products_custom_category(cursor, gtin_string_list, count):
    # get the products and categories from the Trustbox
    sql = "SELECT p.gtin, category.description, sub.description FROM product as p, nwd_main_category as category, nwd_subcategory as sub where p.gtin IN (%s) and p.nwd_main_category_id = category.nwd_main_category_id and p.nwd_subcategory_id is not null and p.nwd_subcategory_id = sub.id and sub.nwd_main_category_id = category.nwd_main_category_id" % gtin_string_list
    cursor.execute(sql)
    rows = cursor.fetchall()
    print("got Trustbox items for user: " + str(count))

    # get the products and categories from the manually added items
    missing_items_sql = "Select item.gtin, main.description, sub.description from missing_trustbox_item as item, nwd_subcategory as sub, nwd_main_category as main where gtin in (%s) and item.nwd_subcategory_id is not null and item.nwd_subcategory_id = sub.id and sub.nwd_main_category_id = main.nwd_main_category_id" % gtin_string_list
    cursor.execute(missing_items_sql)
    missing_rows = cursor.fetchall()
    print("got missing items for user: " + str(count))

    return __generate_product_dict_custom_cats(missing_rows, rows, count)

def __get_products_main_category_with_weights(cursor, gtin_string_list, count):
    # get the products and categories from the Trustbox
    sql = "SELECT p.gtin, category.description, a1.value, a2.value FROM product as p, nwd_main_category as category, product_attribute as a1, product_attribute as a2 where p.gtin IN (%s) and p.nwd_main_category_id = category.nwd_main_category_id and a1.product_id = p.id and a1.canonical_name='packageSize' and isnumeric(a1.value) = 1 and a2.product_id = p.id and a2.canonical_name='packageSize_uom' and (a1.language_code = 'de' or a1.language_code is null) and (a2.language_code = 'de' or a2.language_code is null)" % gtin_string_list
    cursor.execute(sql)
    rows = cursor.fetchall()
    print("got Trustbox items for user: " + str(count))

    # get the products and categories from the manually added items
    missing_items_sql = "Select item.gtin, main.description, item.total_weight from missing_trustbox_item as item, nwd_subcategory as sub, nwd_main_category as main where gtin in (%s) and item.nwd_subcategory_id is not null and item.nwd_subcategory_id = sub.id and sub.nwd_main_category_id = main.nwd_main_category_id" % gtin_string_list
    cursor.execute(missing_items_sql)
    missing_rows = cursor.fetchall()
    print("got missing items for user: " + str(count))

    return __generate_product_dict_weights(missing_rows, rows, count)

def __get_products_main_category_with_weights_custom_cats(cursor, gtin_string_list, count):
    # get the products and categories from the Trustbox
    sql = "SELECT p.gtin, category.description, a1.value, a2.value, sub.description FROM product as p, nwd_main_category as category, nwd_subcategory as sub, product_attribute as a1, product_attribute as a2 where p.gtin IN (%s) and p.nwd_main_category_id = category.nwd_main_category_id and a1.product_id = p.id and a1.canonical_name='packageSize' and isnumeric(a1.value) = 1 and a2.product_id = p.id and a2.canonical_name='packageSize_uom' and (a1.language_code = 'de' or a1.language_code is null) and (a2.language_code = 'de' or a2.language_code is null) and p.nwd_subcategory_id is not null and p.nwd_subcategory_id = sub.id and sub.nwd_main_category_id = category.nwd_main_category_id" % gtin_string_list
    cursor.execute(sql)
    rows = cursor.fetchall()
    print("got Trustbox items for user: " + str(count))

    # get the products and categories from the manually added items
    missing_items_sql = "Select item.gtin, main.description, item.total_weight, sub.description from missing_trustbox_item as item, nwd_subcategory as sub, nwd_main_category as main where gtin in (%s) and item.nwd_subcategory_id is not null and item.nwd_subcategory_id = sub.id and sub.nwd_main_category_id = main.nwd_main_category_id" % gtin_string_list
    cursor.execute(missing_items_sql)
    missing_rows = cursor.fetchall()
    print("got missing items for user: " + str(count))

    return __generate_product_dict_weights_custom_cats(missing_rows, rows, count)

def __get_products_main_category_with_weights_and_salt(cursor, gtin_string_list, count):
    # get the products and categories from the Trustbox
    sql = "SELECT p.gtin, category.description, a1.value, a2.value, fact.amount FROM product as p, nwd_main_category as category, product_attribute as a1, product_attribute as a2, nutrition_fact as fact where p.gtin IN (%s) and p.nwd_main_category_id = category.nwd_main_category_id and a1.product_id = p.id and a1.canonical_name='packageSize' and isnumeric(a1.value) = 1 and a2.product_id = p.id and a2.canonical_name='packageSize_uom' and fact.nutrition_facts_group_id = p.id and fact.amount is not null and ISNUMERIC(fact.amount)= 1 and fact.amount <> '-' and fact.amount <> '0' and fact.canonical_name = 'salt' and category.nwd_main_category_id <> 19 and (a1.language_code = 'de' or a1.language_code is null) and (a2.language_code = 'de' or a2.language_code is null)" % gtin_string_list
    cursor.execute(sql)
    rows = cursor.fetchall()
    print("got Trustbox items for user: " + str(count))

    # get the products and categories from the manually added items
    missing_items_sql = "Select item.gtin, main.description, item.total_weight, item.salt from missing_trustbox_item as item, nwd_subcategory as sub, nwd_main_category as main where gtin in (%s) and item.nwd_subcategory_id is not null and item.nwd_subcategory_id = sub.id and sub.nwd_main_category_id = main.nwd_main_category_id and main.nwd_main_category_id <> 19" % gtin_string_list
    cursor.execute(missing_items_sql)
    missing_rows = cursor.fetchall()
    print("got missing items for user: " + str(count))
    return __generate_product_dict_weights_and_salt(missing_rows, rows, count)

def __get_products_custom_category_with_weights_and_salt(cursor, gtin_string_list, count):
    # get the products and categories from the Trustbox
    sql = "SELECT p.gtin, category.description, a1.value, a2.value, fact.amount, sub.description FROM product as p, nwd_main_category as category, nwd_subcategory as sub, product_attribute as a1, product_attribute as a2, nutrition_fact as fact where p.gtin IN (%s) and p.nwd_subcategory_id = sub.id and p.nwd_main_category_id = category.nwd_main_category_id and a1.product_id = p.id and a1.canonical_name='packageSize' and isnumeric(a1.value) = 1 and a2.product_id = p.id and a2.canonical_name='packageSize_uom' and fact.nutrition_facts_group_id = p.id and fact.amount is not null and ISNUMERIC(fact.amount)= 1 and fact.amount <> '-' and fact.amount <> '0' and fact.canonical_name = 'salt' and category.nwd_main_category_id <> 19 and (a1.language_code = 'de' or a1.language_code is null) and (a2.language_code = 'de' or a2.language_code is null)" % gtin_string_list
    cursor.execute(sql)
    rows = cursor.fetchall()
    print("got Trustbox items for user: " + str(count))

    # get the products and categories from the manually added items
    missing_items_sql = "Select item.gtin, main.description, item.total_weight, item.salt, sub.description from missing_trustbox_item as item, nwd_subcategory as sub, nwd_main_category as main where gtin in (%s) and item.nwd_subcategory_id is not null and item.nwd_subcategory_id = sub.id and sub.nwd_main_category_id = main.nwd_main_category_id and main.nwd_main_category_id <> 19" % gtin_string_list
    cursor.execute(missing_items_sql)
    missing_rows = cursor.fetchall()
    print("got missing items for user: " + str(count))
    return __generate_product_dict_weights_and_salt_custom_cat(missing_rows, rows, count)

def __get_products_minor_category_with_weights(cursor, gtin_string_list, count):
    # get the products and categories from the Trustbox
    sql = "SELECT p.gtin, category.description, a1.value, a2.value FROM product as p, nwd_subcategory as category, product_attribute as a1, product_attribute as a2 where p.gtin IN (%s) and p.nwd_subcategory_id = category.id and a1.product_id = p.id and a1.canonical_name='packageSize' and isnumeric(a1.value) = 1 and a2.product_id = p.id and a2.canonical_name='packageSize_uom' and (a1.language_code = 'de' or a1.language_code is null) and (a2.language_code = 'de' or a2.language_code is null)" % gtin_string_list
    cursor.execute(sql)
    rows = cursor.fetchall()
    print("got Trustbox items for user: " + str(count))

    # get the products and categories from the manually added items
    missing_items_sql = "Select item.gtin, sub.description, item.total_weight from missing_trustbox_item as item, nwd_subcategory as sub where gtin in (%s) and item.nwd_subcategory_id is not null and item.nwd_subcategory_id = sub.id" % gtin_string_list
    cursor.execute(missing_items_sql)
    missing_rows = cursor.fetchall()
    print("got missing items for user: " + str(count))

    return __generate_product_dict_weights(missing_rows, rows, count)


def __get_products_minor_category(cursor, gtin_string_list, count):
    # get the products and categories from the Trustbox
    sql = "SELECT p.gtin, category.description FROM product as p, nwd_subcategory as category where p.gtin IN (%s) and p.nwd_subcategory_id = category.id" % gtin_string_list
    cursor.execute(sql)
    rows = cursor.fetchall()
    print("got Trustbox items for user: " + str(count))

    # get the products and categories from the manually added items
    missing_items_sql = "Select item.gtin, sub.description from missing_trustbox_item as item, nwd_subcategory as sub where gtin in (%s) and item.nwd_subcategory_id is not null and item.nwd_subcategory_id = sub.id" % gtin_string_list
    cursor.execute(missing_items_sql)
    missing_rows = cursor.fetchall()
    print("got missing items for user: " + str(count))

    return __generate_product_dict(missing_rows, rows, count)


""" Aggregate values """

def __create_sorted_spendings_salt(header, relative_spending, user, total_salt):
    # caluclate relative spending
    sorted_spendings = [None] * len(header)
    sorted_spendings[0] = user.pk
    _add_one_time_questions(user, sorted_spendings)
    sorted_spendings[len(sorted_spendings)-1] = results.get_average_salt_per_day(user)
    for cat in relative_spending:
        sorted_spendings[header.index(cat)] = relative_spending[cat]/total_salt
        relative_spending[cat] = 0.0
    return sorted_spendings

def __aggregate_salt(user, basket_items, product_dict, relative_spending, header, count):
    total_salt = 0.0
    # aggregate price for categories
    for basket_item in basket_items:
        product = product_dict.get(basket_item["autoid_scraper_migros_item__gtin"], None)
        if product:
            relative_spending[product["category"]] = relative_spending[product["category"]] + (product["weight"]*product["salt"])
            total_salt = total_salt + (product["weight"]*product["salt"])
    print("aggregated weights for user: " + str(count) + " total salt: " + str(total_salt))
    return __create_sorted_spendings_salt(header, relative_spending, user, total_salt)


def __aggregate_weights(user, basket_items, product_dict, relative_spending, header, count):
    total_weight = 0.0
    # aggregate price for categories
    for basket_item in basket_items:
        product = product_dict.get(basket_item["autoid_scraper_migros_item__gtin"], None)
        if product:
            relative_spending[product["category"]] = relative_spending[product["category"]] + product["weight"]
            total_weight = total_weight + product["weight"]
    print("aggregated weights for user: " + str(count) + " total weight: " + str(total_weight))
        
    # caluclate relative spending
    sorted_spendings = [None] * len(header)
    sorted_spendings[0] = user.pk
    _add_one_time_questions(user, sorted_spendings)
    sorted_spendings[len(sorted_spendings)-1] = results.get_average_salt_per_day(user)
    for cat in relative_spending:
        sorted_spendings[header.index(cat)] = relative_spending[cat]/total_weight
        relative_spending[cat] = 0.0
    return sorted_spendings

def __aggregate_prices(user, basket_items, product_dict, relative_spending, header,volumne_of_sales, count):
    # aggregate price for categories
    for basket_item in basket_items:
        category = product_dict.get(basket_item["autoid_scraper_migros_item__gtin"], None)
        if category:
            #category = category.encode("utf8")
            relative_spending[category] = relative_spending[category] + basket_item["price"]
    print("aggregated prices for user: " + str(count))
        
    # caluclate relative spending
    sorted_spendings = [None] * len(header)
    sorted_spendings[0] = user.pk
    _add_one_time_questions(user, sorted_spendings)
    sorted_spendings[len(sorted_spendings)-1] = results.get_average_salt_per_day(user)
    for cat in relative_spending:
        sorted_spendings[header.index(cat)] = relative_spending[cat]/volumne_of_sales["price__sum"]
        relative_spending[cat] = 0.0
    return sorted_spendings

def __aggregate_prices_custom(user, basket_items, product_dict, relative_spending, header,volumne_of_sales, count):
    # aggregate price for categories
    for basket_item in basket_items:
        product = product_dict.get(basket_item["autoid_scraper_migros_item__gtin"], None)
        if product:
            category = __add_to_custom_category(relative_spending, product, product["category"], product["sub_cat"])
            #category = category.encode("utf8")
            relative_spending[category] = relative_spending[category] + basket_item["price"]
    print("aggregated prices for user: " + str(count))
        
    # caluclate relative spending
    sorted_spendings = [None] * len(header)
    sorted_spendings[0] = user.pk
    _add_one_time_questions(user, sorted_spendings)
    sorted_spendings[len(sorted_spendings)-1] = results.get_average_salt_per_day(user)
    for cat in relative_spending:
        sorted_spendings[header.index(cat)] = relative_spending[cat]/volumne_of_sales["price__sum"]
        relative_spending[cat] = 0.0
    return sorted_spendings


def get_data_for_regression_model_1(users, response):
    cursor, cvs_data, header, relative_spending, writer, response = __main_category_setup(response)
    count = 1
    for user in users:
        print("starting processing user: " + str(count))
        # get the total budget spent on food items with loyalty card
        volumne_of_sales = __get_volume_of_sales(user)
        
        # get all purchased items and their respective gtins as list, needed because the different tables are in different databases and Django does not support queries over multiple databases on Azure
        basket_items, gtin_string_list = __get_purchased_products(user)
        print("got purhcased items for user: " + str(count))
        if len(gtin_string_list) > 0:
            product_dict = __get_products_main_category(cursor, gtin_string_list, count)
        
            sorted_spendings = __aggregate_prices(user.user, basket_items, product_dict, relative_spending, header,volumne_of_sales, count)

            print("finished processing user: " + str(count))
            count = count + 1
            writer.writerow(sorted_spendings)
    return response

def get_data_for_regression_model_2(users, response):
    cursor, cvs_data, header, relative_spending, writer, response = __minor_category_setup(response)
    count = 1
    for user in users:
        print("starting processing user: " + str(count))
        # get the total budget spent on food items with loyalty card
        volumne_of_sales = __get_volume_of_sales(user)
        
        # get all purchased items and their respective gtins as list, needed because the different tables are in different databases and Django does not support queries over multiple databases on Azure
        basket_items, gtin_string_list = __get_purchased_products(user)
        print("got purhcased items for user: " + str(count))
        if len(gtin_string_list) > 0:
            product_dict = __get_products_minor_category(cursor, gtin_string_list, count)
        
            sorted_spendings = __aggregate_prices(user.user, basket_items, product_dict, relative_spending, header,volumne_of_sales, count)

            print("finished processing user: " + str(count))
            count = count + 1
            writer.writerow(sorted_spendings)
    return response


def get_data_for_regression_model_3(users, response):
    cursor, cvs_data, header, relative_spending, writer, response = __main_category_setup(response)
    count = 1
    for user in users:
        print("starting processing user: " + str(count))

        # get all purchased items and their respective gtins as list
        basket_items, gtin_string_list = __get_purchased_products(user)
        print("got purhcased items for user: " + str(count))
        if len(gtin_string_list) > 0:
            product_dict = __get_products_main_category_with_weights(cursor, gtin_string_list, count)
        
            sorted_spendings = __aggregate_weights(user.user, basket_items, product_dict, relative_spending, header,count)

            print("finished processing user: " + str(count))
            count = count + 1
            writer.writerow(sorted_spendings)
    return response

def get_data_for_regression_model_4(users, response):
    cursor, cvs_data, header, relative_spending, writer, response = __minor_category_setup(response)
    count = 1
    for user in users:
        print("starting processing user: " + str(count))

        # get all purchased items and their respective gtins as list
        basket_items, gtin_string_list = __get_purchased_products(user)
        print("got purhcased items for user: " + str(count))
        if len(gtin_string_list) > 0:
            product_dict = __get_products_minor_category_with_weights(cursor, gtin_string_list, count)
        
            sorted_spendings = __aggregate_weights(user.user, basket_items, product_dict, relative_spending, header,count)

            print("finished processing user: " + str(count))
            count = count + 1
            writer.writerow(sorted_spendings)
    return response

def get_data_for_regression_model_5(users, response):
    cursor, cvs_data, header, relative_spending, writer, response = __main_category_setup(response)
    count = 1
    for user in users:
        print("starting processing user: " + str(count))

        # get all purchased items and their respective gtins as list
        basket_items, gtin_string_list = __get_purchased_products(user)
        print("got purhcased items for user: " + str(count))
        if len(gtin_string_list) > 0:
            product_dict = __get_products_main_category_with_weights_and_salt(cursor, gtin_string_list, count)
        
            sorted_spendings = __aggregate_salt(user.user, basket_items, product_dict, relative_spending, header,count)

            print("finished processing user: " + str(count))
            count = count + 1
            writer.writerow(sorted_spendings)
    return response

def get_data_for_regression_model_6(users, response):
    cursor, cvs_data, header, relative_spending, writer, response = __main_category_setup(response)
    count = 1
    for user in users:
        print("starting processing user: " + str(count))

        # get all purchased items and their respective gtins as list
        basket_items, gtin_string_list = __get_purchased_products(user)
        print("got purhcased items for user: " + str(count))
        if len(gtin_string_list) > 0:
            product_dict = __get_products_main_category_with_weights_and_salt(cursor, gtin_string_list, count)

            average_product_salt_dict = {}

            for cat in relative_spending:
                average_product_salt_dict[cat] = {}
                average_product_salt_dict[cat]["numberOfProducts"] = 0
                average_product_salt_dict[cat]["total_salt"] = 0.0
                average_product_salt_dict[cat]["averageSalt"] = 0.0

            # aggregate price for categories
            for basket_item in basket_items:
                product = product_dict.get(basket_item["autoid_scraper_migros_item__gtin"], None)
                if product:
                    average_product_salt_dict[product["category"]]["total_salt"] = average_product_salt_dict[product["category"]]["total_salt"] + product["salt"]
                    average_product_salt_dict[product["category"]]["numberOfProducts"] = average_product_salt_dict[product["category"]]["numberOfProducts"] + 1
            
            for cat in average_product_salt_dict:
                if average_product_salt_dict[cat]["numberOfProducts"]> 0:
                    average_product_salt_dict[cat]["averageSalt"] = average_product_salt_dict[cat]["total_salt"] / average_product_salt_dict[cat]["numberOfProducts"]



            sorted_spendings = [None] * len(header)
            sorted_spendings[0] = user.pk
            _add_one_time_questions(user.user, sorted_spendings)
            sorted_spendings[len(sorted_spendings)-1] = results.get_average_salt_per_day(user.user)
            for cat in average_product_salt_dict:
                sorted_spendings[header.index(cat)] = average_product_salt_dict[cat]["averageSalt"]
        
            print("finished processing user: " + str(count))
            count = count + 1
            writer.writerow(sorted_spendings)

    return response


def __add_to_custom_category(relative_spending, product, main_cat_name, sub_cat_name):
    if main_cat_name in relative_spending:
       return main_cat_name
    else:
        if sub_cat_name == u"Brote und Brotwaren" or sub_cat_name == u"Knäckebrote, Zwieback, Crackers und Waffeln":
            return "Brote"
        elif sub_cat_name == u"Flocken, Kleie und Keime" or sub_cat_name == u"Müeslimischungen und Frühstückscerealien":
            return "Flocken und Cerealien"
        elif sub_cat_name == u"Brühwurstware" or sub_cat_name == u"Kochwurstware" or sub_cat_name == u"Rohwurstware" or sub_cat_name == u"Sonstige Fleisch- und Wurstwaren":
            return "Wuerste" 
        elif sub_cat_name == u"Geflügel" or sub_cat_name == u"Kalb" or sub_cat_name == u"Lamm, Schaf" or sub_cat_name == u"Rind" or sub_cat_name == u"Schwein" or sub_cat_name == u"Wild" or sub_cat_name == u"Sonstige Tierarten":
            return "Fleich"
        elif sub_cat_name == u"Frischkäse und Quark" or sub_cat_name == u"Hartkäse" or sub_cat_name == u"Käseerzeugnisse" or sub_cat_name == u"Weichkäse":
            return "Kaese"
        elif sub_cat_name == u"Milch" or sub_cat_name == u"Milchersatzprodukte" or sub_cat_name == u"Milch- und Joghurtgetränke" or sub_cat_name == u"Rahm und Butter" or sub_cat_name == u"Joghurt und Sauermilch":
            return "Milch"

def get_data_for_regression_model_5_custom_cat(users, response):
    cursor, cvs_data, header, relative_spending, writer, response = __custom_category_setup(response)
    count = 1
    for user in users:
        print("starting processing user: " + str(count))

        # get all purchased items and their respective gtins as list
        basket_items, gtin_string_list = __get_purchased_products(user)
        print("got purhcased items for user: " + str(count))
        if len(gtin_string_list) > 0:
            product_dict = __get_products_custom_category_with_weights_and_salt(cursor, gtin_string_list, count)
            total_salt = 0.0
            for basket_item in basket_items:
                product = product_dict.get(basket_item["autoid_scraper_migros_item__gtin"], None)
                if product:
                    category = __add_to_custom_category(relative_spending, product, product["category"], product["sub_cat"])
                    relative_spending[category] = relative_spending[category] + (product["weight"]*product["salt"])
                    total_salt = total_salt + (product["weight"]*product["salt"])
            sorted_spendings = __create_sorted_spendings_salt(header, relative_spending, user.user, total_salt)

            print("finished processing user: " + str(count))
            count = count + 1
            writer.writerow(sorted_spendings)
    return response

def get_data_for_regression_model_6_custom_cat(users, response):
    cursor, cvs_data, header, relative_spending, writer, response = __custom_category_setup(response)
    count = 1
    for user in users:
        print("starting processing user: " + str(count))

        # get all purchased items and their respective gtins as list
        basket_items, gtin_string_list = __get_purchased_products(user)
        print("got purhcased items for user: " + str(count))
        if len(gtin_string_list) > 0:
            product_dict = __get_products_custom_category_with_weights_and_salt(cursor, gtin_string_list, count)
            average_product_salt_dict = {}

            for cat in relative_spending:
                average_product_salt_dict[cat] = {}
                average_product_salt_dict[cat]["numberOfProducts"] = 0
                average_product_salt_dict[cat]["total_salt"] = 0.0
                average_product_salt_dict[cat]["averageSalt"] = 0.0

            # aggregate price for categories
            for basket_item in basket_items:
                product = product_dict.get(basket_item["autoid_scraper_migros_item__gtin"], None)
                if product:
                    category = __add_to_custom_category(average_product_salt_dict, product, product["category"], product["sub_cat"])
                    average_product_salt_dict[category]["total_salt"] = average_product_salt_dict[category]["total_salt"] + product["salt"]
                    average_product_salt_dict[category]["numberOfProducts"] = average_product_salt_dict[category]["numberOfProducts"] + 1
            
            for cat in average_product_salt_dict:
                if average_product_salt_dict[cat]["numberOfProducts"]> 0:
                    average_product_salt_dict[cat]["averageSalt"] = average_product_salt_dict[cat]["total_salt"] / average_product_salt_dict[cat]["numberOfProducts"]

            sorted_spendings = [None] * len(header)
            sorted_spendings[0] = user.pk
            _add_one_time_questions(user.user, sorted_spendings)
            sorted_spendings[len(sorted_spendings)-1] = results.get_average_salt_per_day(user.user)
            for cat in average_product_salt_dict:
                sorted_spendings[header.index(cat)] = average_product_salt_dict[cat]["averageSalt"]

            print("finished processing user: " + str(count))
            count = count + 1
            writer.writerow(sorted_spendings)
    return response

def get_data_for_regression_model_1_custom_cat(users, response):
    cursor, cvs_data, header, relative_spending, writer, response = __custom_category_setup(response)
    count = 1
    for user in users:
        volumne_of_sales = __get_volume_of_sales(user)
        
        # get all purchased items and their respective gtins as list, needed because the different tables are in different databases and Django does not support queries over multiple databases on Azure
        basket_items, gtin_string_list = __get_purchased_products(user)
        print("got purhcased items for user: " + str(count))
        if len(gtin_string_list) > 0:
            product_dict = __get_products_custom_category(cursor, gtin_string_list, count)
        
            sorted_spendings = __aggregate_prices_custom(user.user, basket_items, product_dict, relative_spending, header,volumne_of_sales, count)

            print("finished processing user: " + str(count))
            count = count + 1
            writer.writerow(sorted_spendings)
    return response

def get_data_for_regression_model_3_custom_cats(users, response):
    cursor, cvs_data, header, relative_spending, writer, response = __custom_category_setup(response)
    count = 1
    for user in users:
        print("starting processing user: " + str(count))

        # get all purchased items and their respective gtins as list
        basket_items, gtin_string_list = __get_purchased_products(user)
        print("got purhcased items for user: " + str(count))
        if len(gtin_string_list) > 0:
            product_dict = __get_products_main_category_with_weights_custom_cats(cursor, gtin_string_list, count)
            for product in product_dict:
                product_dict[product]["category"] = __add_to_custom_category(relative_spending, product_dict[product], product_dict[product]["category"], product_dict[product]["sub_cat"])
            sorted_spendings = __aggregate_weights(user.user, basket_items, product_dict, relative_spending, header,count)

            print("finished processing user: " + str(count))
            count = count + 1
            writer.writerow(sorted_spendings)
    return response


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False