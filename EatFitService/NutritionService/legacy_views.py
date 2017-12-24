from rest_framework.decorators import api_view, permission_classes
from NutritionService.helpers import store_image
from NutritionService.views import create_product
from TrustBoxAPI.serializer import ProductImportSerializer
from TrustBoxAPI.models import NwdSubcategory
from NutritionService.models import NutritionFact
import requests
from NutritionService.models import MajorCategory
from NutritionService.models import MinorCategory
from TrustBoxAPI.models import NwdMainCategory
from TrustBoxAPI.models import Product as TrustboxProduct
from NutritionService.models import Product
from rest_framework.response import Response
from TrustBoxAPI.models import MissingTrustboxItem
from rest_framework import permissions
from django.db import connection
from django.core.files.base import ContentFile
import tempfile
from django.core import files
import random
import string
import json


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def import_categories(request):
    main_categories = NwdMainCategory.objects.using("eatfit").all()
    minor_categories = NwdSubcategory.objects.using("eatfit").all()

    major_cat_dict = {}

    for cat in main_categories:
        major_category = MajorCategory.objects.create(id = cat.pk, description = cat.description)
        major_cat_dict[major_category.pk] = major_category

    for cat in minor_categories:
        minor_category = MinorCategory.objects.create(id = cat.pk, description = cat.description, nwd_subcategory_id = cat.nwd_subcategory_id, category_major = major_cat_dict[cat.nwd_main_category.pk])
        """
        new_file = ContentFile(cat.icon.read())
        new_file.name = cat.icon.name
        minor_category.icon = new_file
        minor_category.save()
        """
    return Response()

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def import_missing_products(request):
    major_cat_dict, minor_cat_dict = __get_categories()
    gtins = MissingTrustboxItem.objects.using("eatfit").values_list("gtin", flat=True)
    legacy_gtin_set = set()
    existing_gtin_set = set()
    for gtin  in gtins:
        legacy_gtin_set.add(gtin)
    print("collected legacy gtins")
    existing_gtins = Product.objects.all().values_list("gtin", flat=True)
    for gtin in existing_gtins:
        existing_gtin_set.add(gtin)
    print("collected existing gtins")
    missing_gtins = legacy_gtin_set.difference(existing_gtin_set)
    print("# missing gtins: " + str(len(missing_gtins)))

    missing_products = MissingTrustboxItem.objects.using("eatfit").filter(gtin__in = list(missing_gtins))

    count = 0
    for missing_product in missing_products:
        product = Product()
        product.gtin = missing_product.gtin
        product.product_name_de = missing_product.name
        product.product_size = str(missing_product.total_weight)
        product.serving_size = str(missing_product.serving_size)
        if missing_product.nwd_subcategory:
            minor_cat = minor_cat_dict[missing_product.nwd_subcategory.nwd_subcategory_id]
            product.minor_category = minor_cat
        product.save()
        if missing_product.image_url:
            store_image(missing_product.image_url, product)
        
        nutrition_facts_to_create = []
        nutrition_fact1 = NutritionFact(product = product, name = "salt", amount = missing_product.salt, unit_of_measure = "g")
        nutrition_facts_to_create.append(nutrition_fact1)

        nutrition_fact2 = NutritionFact(product = product, name = "sodium", amount = missing_product.sodium, unit_of_measure = "g")
        nutrition_facts_to_create.append(nutrition_fact2)

        nutrition_fact3 = NutritionFact(product = product, name = "energyKJ", amount = missing_product.energy, unit_of_measure = "KJ")
        nutrition_facts_to_create.append(nutrition_fact3)

        nutrition_fact4 = NutritionFact(product = product, name = "totalFat", amount = missing_product.fat, unit_of_measure = "g")
        nutrition_facts_to_create.append(nutrition_fact4)

        nutrition_fact5 = NutritionFact(product = product, name = "saturatedFat", amount = missing_product.saturated_fat, unit_of_measure = "g")
        nutrition_facts_to_create.append(nutrition_fact5)

        nutrition_fact6 = NutritionFact(product = product, name = "totalCarbohydrate", amount = missing_product.carbohydrate, unit_of_measure = "g")
        nutrition_facts_to_create.append(nutrition_fact6)

        nutrition_fact7 = NutritionFact(product = product, name = "sugars", amount = missing_product.sugar, unit_of_measure = "g")
        nutrition_facts_to_create.append(nutrition_fact7)

        nutrition_fact8 = NutritionFact(product = product, name = "dietaryFiber", amount = missing_product.fibers, unit_of_measure = "g")
        nutrition_facts_to_create.append(nutrition_fact8)

        nutrition_fact9 = NutritionFact(product = product, name = "protein", amount = missing_product.protein, unit_of_measure = "g")
        nutrition_facts_to_create.append(nutrition_fact9)

        NutritionFact.objects.bulk_create(nutrition_facts_to_create)
        count = count + 1
        print("created product #: " + str(count))

    return Response()



@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def import_trustbox_products(request):
    major_cat_dict, minor_cat_dict = __get_categories()
    gtins = TrustboxProduct.objects.using("eatfit").values_list("gtin", flat=True)
    legacy_gtin_set = set()
    existing_gtin_set = set()
    for gtin  in gtins:
        legacy_gtin_set.add(gtin)
    print("collected legacy gtins")
    existing_gtins = Product.objects.all().values_list("gtin", flat=True)
    for gtin in existing_gtins:
        existing_gtin_set.add(gtin)
    print("collected existing gtins")
    missing_gtins = legacy_gtin_set.difference(existing_gtin_set)
    print("# missing gtins: " + str(len(missing_gtins)))
    gtin_string_list = ",".join(str(gtin) for gtin in missing_gtins)
    sql = 'SELECT top(1200) * FROM product where gtin in (%s)' % gtin_string_list
    missing_products = TrustboxProduct.objects.using("eatfit").raw(sql)
    count = 0
    for missing_product in missing_products:
        serializer = ProductImportSerializer(missing_product)
        create_product(serializer.data)
        count = count + 1
        print("created product #: " + str(count))

    return Response()

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def categorize_products(request):
    major_cat_dict, minor_cat_dict = __get_categories()
    gtins = TrustboxProduct.objects.using("eatfit").filter(nwd_main_category__isnull = False).values_list("gtin", flat=True)
    legacy_gtin_set = set()
    existing_gtin_set = set()
    for gtin  in gtins:
        legacy_gtin_set.add(gtin)
    print("collected legacy gtins")
    existing_gtins = Product.objects.filter(major_category__isnull=True).values_list("gtin", flat=True)
    for gtin in existing_gtins:
        existing_gtin_set.add(gtin)
    print("collected existing gtins")
    categorized_gtins = legacy_gtin_set.intersection(existing_gtin_set)
    print("# uncategorized gtins: " + str(len(categorized_gtins)))
    gtin_string_list = ",".join(str(gtin) for gtin in categorized_gtins)
    sql = 'SELECT top(1000) * FROM product where gtin in (%s)' % gtin_string_list
    categorized_products = TrustboxProduct.objects.using("eatfit").raw(sql)
    uncategroized_products = Product.objects.filter(gtin__in = categorized_gtins)
    uncategorized_products_dict = {}
    for uncategroized_product in uncategroized_products:
        uncategorized_products_dict[uncategroized_product.gtin] = uncategroized_product
    count = 0
    for categorized_product in categorized_products:
        updated = False
        uncategroized_product = uncategorized_products_dict[categorized_product.gtin]
        if categorized_product.nwd_main_category:
            uncategroized_product.major_category = major_cat_dict[categorized_product.nwd_main_category.pk]
            updated = True
        if categorized_product.nwd_subcategory:
            uncategroized_product.minor_category = minor_cat_dict[categorized_product.nwd_subcategory.nwd_subcategory_id]
            updated = True
        if updated:
            uncategroized_product.save()

        count = count + 1
        print("categorized product #: " + str(count))

    return Response()



def __get_categories():
    major_categories = MajorCategory.objects.all()
    minor_categories = MinorCategory.objects.all()

    major_cat_dict = {}
    minor_cat_dict = {}

    for cat in major_categories:
        major_cat_dict[cat.id] = cat

    for cat in minor_categories:
        minor_cat_dict[cat.nwd_subcategory_id] = cat

    return major_cat_dict, minor_cat_dict
