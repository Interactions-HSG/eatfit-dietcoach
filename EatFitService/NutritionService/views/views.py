# -*- coding: utf-8 -*-

"""
Definition of views.
"""

from EatFitService.settings import TRUSTBOX_USERNAME, TRUSTBOX_PASSWORD, TRUSTBOX_URL
from NutritionService import data_cleaning
from NutritionService import reports
from NutritionService.codecheck_integration.codecheck import import_from_codecheck
from django.shortcuts import get_object_or_404
from NutritionService.helpers import calculate_ofcom_value
from NutritionService.helpers import store_image
from django.http.response import HttpResponseForbidden
from rest_framework import permissions
from rest_framework.decorators import permission_classes
from datetime import datetime
from NutritionService.models import ImportLog
from suds.client import Client
from suds.sudsobject import asdict
from django.http import HttpResponse
from NutritionService.models import Product, Allergen, NutritionFact, Ingredient, NotFoundLog, ErrorLog
from NutritionService.serializers import ProductSerializer
from NutritionService.tasks import import_from_openfood
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
import tempfile
from django.core import files
import random
import string


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def report_product(request):
    """
    Reports a given product. A new entry in the DB is created for every request so duplication is allowed.
    Example request: POST /product/report/
                     body data: {"gtin":"123123",
                                 "app": "TestApp",
                                 "error_description": "I am just here for the testing"}
    :param request: Request made by the user. Must include in the body 'gtin', 'app' and 'error_description'.
    :return: Status 200 and 'success' (bool) if everything was okay.
    """
    try:
        app = request.data['app']
    except KeyError:
        return_data = {'success': False,
                       'error': 'Name of the app is missing from the request body. Field name should be called "app"'}
        return Response(return_data, status=200)  # Should return 400 :(
    try:
        gtin = request.data['gtin']
    except KeyError:
        return_data = {'success': False,
                       'error': 'GTIN of product is missing from the request body. Field name should be called "gtin"'}
        return Response(return_data, status=200)  # Should return 400 :(
    try:
        error_description = request.data['error_description']
    except KeyError:
        return_data = {'success': False,
                       'error': 'Error description is missing from the request body. '
                                'Field name should be called "error_description"'}
        return Response(return_data, status=200)  # Should return 400 :(

    # Create a new entry in the database.
    ErrorLog.objects.create(reporting_app=app, gtin=gtin, error_description=error_description)

    # TODO: Should we return the error log db entry created as part of the response?
    return Response({'success': True}, status=200)


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def report_missing_gtin(request):
    """
    Reports a given gtin is missing. The view first checks if an entry already exists for this gtin and if there is
    such one, the count is incremented by one and saved. If such gtin is not found, a new entry is created with the
    gtin and the count is set to 1.
    Example request: POST /product/missing/
                     body data: {"gtin":"1234567891"}
    :param request: Request made by the user. Must include in the body 'gtin'.
    :return: Status 200 and 'success' (bool) if everything was okay.
    """
    try:
        gtin = request.data['gtin']
    except KeyError:
        return_data = {'success': False,
                       'error': 'GTIN of product is missing from the request body. Field name should be called "gtin"'}
        return Response(return_data, status=200)  # Should return 400. Django is sad :(

    not_found_log, created = NotFoundLog.objects.get_or_create(gtin=gtin)
    if not created:
        # An entry with this gtin already exists so we only increment and the count value
        not_found_log.count = not_found_log.count + 1
        not_found_log.save()
    # Else if a new one is created, the count is set to 1 by default (check model definition in models.py).

    # TODO: Should we return the not found db entry as part of the response?
    return Response({'success': True}, status=200)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_product(request, gtin):
    """
    Get product information given gtin
    returns sucess and object

    query param: resultType, values: 'array', 'dictionary'
    """
    result_type = request.GET.get("resultType", "array")
    products = Product.objects.filter(gtin=gtin)
    if not products.exists():
        l, created = NotFoundLog.objects.get_or_create(gtin=gtin)
        if not created:
            l.count = l.count + 1
            l.save()
        result = {}
        result["success"] = False
        result["products"] = None
        return Response(result)
    else:
        serializer = ProductSerializer(products, many=True)
        result = {}
        result["success"] = True
        if result_type == "array":
            result["products"] = serializer.data
        else:
            result["products"] = []
            for p in serializer.data:
                result["products"].append(__change_product_objects(p))
    return Response(result)


def __change_product_objects(product):
    result_product = {}
    result_product["gtin"] = product["gtin"]
    result_product["producer"] = product["producer"]
    result_product["product_size"] = product["product_size"]
    result_product["product_size_unit_of_measure"] = product["product_size_unit_of_measure"]
    result_product["serving_size"] = product["serving_size"]
    result_product["comment"] = product["comment"]
    result_product["image"] = product["image"]
    result_product["major_category"] = product["major_category"]
    result_product["ofcom_value"] = product["ofcom_value"]
    result_product["product_names"] = {}
    result_product["product_names"]["en"] = product["product_name_en"]
    result_product["product_names"]["de"] = product["product_name_de"]
    result_product["product_names"]["fr"] = product["product_name_fr"]
    result_product["product_names"]["it"] = product["product_name_it"]
    result_product["allergens"] = []
    result_product["nutrients"] = {}
    result_product["ingredients"] = {}
    for a in product["allergens"]:
        result_product["allergens"].append(a)
    for n in product["nutrients"]:
        result_product["nutrients"][n["name"]] = {}
        result_product["nutrients"][n["name"]]["amount"] = n["amount"]
        result_product["nutrients"][n["name"]]["unit_of_measure"]  = n["unit_of_measure"]
    for i in product["ingredients"]:
        result_product["ingredients"][i["lang"]] = i["text"]
    return result_product


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_better_products(request, gtin):
    """
    query param: sortBy, values: 'ofcomValue', 'energyKJ', 'totalFat', 'saturatedFat', 'salt', 'sugars', 'protein',
                                 'totalCarbohydrate', 'dietaryFiber', 'healthPercentage' - this is the fruit and veg %,
                                 'sodium'
    query param: resultType, values: 'array', 'dictionary'
    """

    product = get_object_or_404(Product.objects.all(), gtin = gtin)
    sort_by = request.GET.get("sortBy", "ofcomValue")
    result_type = request.GET.get("resultType", "array")
    number_of_results = 20
    results_found = 0
    products = []
    better_products_minor = []
    better_products_major = []
    if product.minor_category:
        if sort_by == "ofcomValue":
            better_products_minor = Product.objects.filter(minor_category=product.minor_category).order_by("ofcom_value")[:number_of_results]
            results_found = better_products_minor.count()
        elif sort_by == 'healthPercentage':
            better_products_minor = Product.objects.filter(minor_category=product.minor_category).order_by("health_percentage")[:number_of_results]
            results_found = better_products_minor.count()
        else:
            better_products_minor = Product.objects.raw("Select p.* from product as p, nutrition_fact as n where n.product_id = p.id and p.minor_category_id = %s and n.name = %s order by n.amount", [product.minor_category.pk, sort_by])[:number_of_results]
            results_found = len(better_products_minor)
       
    if results_found < number_of_results and product.major_category:
        if sort_by == "ofcomValue":
            better_products_major = Product.objects.filter(major_category = product.major_category).order_by("ofcom_value")[:(number_of_results-results_found)]
            results_found = better_products_major.count()
        elif sort_by == 'healthPercentage':
            better_products_major = Product.objects.filter(major_category = product.major_category).order_by("health_percentage")[:(number_of_results-results_found)]
            results_found = better_products_major.count()
        else:
            better_products_major = Product.objects.raw("Select p.* from product as p, nutrition_fact as n where n.product_id = p.id and p.major_category_id = %s and n.name = %s order by n.amount", [product.major_category.pk, sort_by])[:(number_of_results-results_found)]
            results_found = len(better_products_major)
    for p in better_products_minor:
        products.append(p)
    for p in better_products_major:
        products.append(p)
    if results_found > 0:
        serializer = ProductSerializer(products, many=True)
        result = {}
        result["success"] = True
        if result_type == "array":
            result["products"] = serializer.data
        else:
            result["products"] = []
            for p in serializer.data:
                result["products"].append(__change_product_objects(p))
    else:
        result = {}
        result["success"] = False
        result["products"] = None
    return Response(result)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def update_database(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    """ checks for changes since last update and adds new objects"""
    last_updated='2000-01-01T00:00:00Z'
    import_log_queryset = ImportLog.objects.filter(import_finished__isnull=False).order_by("-import_finished")[:1]
    if import_log_queryset.exists():
        last_updated = import_log_queryset[0].import_finished.strftime("%Y-%m-%dT%H:%M:%SZ")
    __update_objects_from_trustbox(last_updated)
    return HttpResponse(status = 200)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_products_from_openfood(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    import_from_openfood()
    return HttpResponse(status = 200)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_products_from_codecheck(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    import_from_codecheck()
    return HttpResponse(status = 200)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def calculate_ofcom_values(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    count = 0
    for product in Product.objects.filter(ofcom_value__isnull=True):
        calculate_ofcom_value(product)
        count = count + 1
        print("calculated for product: " + str(count))
    return Response(status = 200)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def generate_status_report(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    reports.generate_daily_report()
    return Response(status = 200)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def data_clean_task(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    data_cleaning.clean_salt_sodium()
    return Response(status = 200)


def __update_objects_from_trustbox(last_updated):
    """
    Takes date of last updated and creates new and changed objects
    """
    client = Client(TRUSTBOX_URL)
    response = client.service.getChangedArticles(last_updated, TRUSTBOX_USERNAME, TRUSTBOX_PASSWORD)
    updated_gtins = [article['gtin'] for article in __recursive_translation(response)["article"]]
    import_log = ImportLog.objects.create(import_started = datetime.now())
    count = 0
    for gtin in updated_gtins:
        count = count + 1
        result = client.service.getTrustedDataByGTIN(gtin, TRUSTBOX_USERNAME, TRUSTBOX_PASSWORD)
        __soap_response_to_objects(result)
        #print("imported model: " + str(count))
    import_log.import_finished = datetime.now()
    import_log.save()

# to be optimized -- objects can be created in batches 
def __soap_response_to_objects(response):
    """
    Takes SOAP response from TRUSTBOX, crates and save object in DB.
    Create Object and save in same method due to fg-keys constraints.
    """
    result_as_dict = __recursive_translation(response)
    products = result_as_dict['productList'][0]['products']
    for p in products:
        create_product(p)

def __recursive_translation(d):
    ### helper method to translate SOAP response to dictionary ###
    result = {}
    for k, v in asdict(d).iteritems():
        if hasattr(v, '__keylist__'):
            result[k] = __recursive_translation(v)
        elif isinstance(v, list):
            result[k] = []
            for item in v:
                if hasattr(item, '__keylist__'):
                    result[k].append(__recursive_translation(item))
                else:
                    result[k].append(item)
        else:
            result[k] = v
    return result



def create_product(p):
    try:
        default_arguments = {}
        temp_image_url = None
        for n in p['productNames']:
            if n['_languageCode'] == "de":
                default_arguments["product_name_de"] = unicode(n['name'])
            if n['_languageCode'] == "fr":
                default_arguments["product_name_fr"] = unicode(n['name'])
            if n['_languageCode'] == "en":
                default_arguments["product_name_en"] = unicode(n['name'])
            if n['_languageCode'] == "it":
                default_arguments["product_name_it"] = unicode(n['name'])
        for attr in p['productAttributes']:
            try:
                if attr['_canonicalName'] == 'manufacturer':
                    default_arguments["producer"] = unicode(attr['value'])
                if attr['_canonicalName'] == 'packageSize':
                    default_arguments["product_size"] = attr['value']
                if attr['_canonicalName'] == 'packageSize_uom':
                    default_arguments["product_size_unit_of_measure"] = attr['value']
                if attr['_canonicalName'] == 'productImageURL':
                    temp_image_url = attr['value']
            except:
                continue
        if 'nutritionGroupAttributes' in p['nutrition']['nutritionFactsGroups']:
            for attr in p['nutrition']['nutritionFactsGroups']['nutritionGroupAttributes']:
                if attr['_canonicalName'] == 'servingSize' and attr['value'] != "0.0": 
                    #check against 0 due to multiple entries with different values
                    default_arguments["serving_size"] = attr['value']
        default_arguments["source"] = Product.TRUSTBOX
        default_arguments["source_checked"] = True
        product, created = Product.objects.update_or_create(gtin = p['_gtin'], defaults = default_arguments)
        if temp_image_url:
            store_image(temp_image_url, product)

        # create nutrition facts for products
        if 'nutritionFacts' in p['nutrition']['nutritionFactsGroups']:
            for attr in p['nutrition']['nutritionFactsGroups']['nutritionFacts']:
                try:
                    is_a_number, number = is_number(attr['amount'])
                    if is_a_number:
                        default_arguments = {}
                        default_arguments["amount"] = number 
                        default_arguments["unit_of_measure"] = attr['unitOfMeasure'] 
                        NutritionFact.objects.update_or_create(product = product, name  = attr["_canonicalName"], defaults = default_arguments)
                except: #ignore shitty data quality
                    continue
        
        # create allergens and ingridients for products
        for attr in p['nutrition']['nutritionAttributes']:
            if attr['_canonicalName'].startswith('allergen') and attr['value'] != "false" and attr['value'] != 'unknown':
                Allergen.objects.update_or_create(product = product, name = attr["_canonicalName"], defaults = {"certainity" : attr['value']})
            if attr['_canonicalName'] == 'ingredients':
                Ingredient.objects.update_or_create(product = product, lang = attr["_languageCode"], defaults = {"text" : unicode(attr['value'])})
        calculate_ofcom_value(product)
    except Exception as e:
        print(e)

def is_number(s):
    try:
        v = float(s)
        return True, v 
    except ValueError:
        return False, None