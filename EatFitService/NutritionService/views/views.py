# -*- coding: utf-8 -*-

"""
Definition of views.
"""

from __future__ import print_function, division
from datetime import datetime
import logging
from suds.client import Client
from suds.sudsobject import asdict

from django.http import HttpResponse
from django.http.response import HttpResponseForbidden
from django.shortcuts import get_object_or_404

from rest_framework import permissions
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response

from EatFitService.settings import TRUSTBOX_USERNAME, TRUSTBOX_PASSWORD, TRUSTBOX_URL
from NutritionService import data_cleaning, reports
from NutritionService.codecheck_integration.codecheck import import_from_codecheck
from NutritionService.helpers import store_image, download_csv
from NutritionService.models import DigitalReceipt, NonFoundMatching, Matching, MajorCategory, MinorCategory, \
    HealthTipp, ImportLog, Product, Allergen, NutritionFact, Ingredient, NotFoundLog, ErrorLog, \
    ReceiptToNutritionUser, calculate_ofcom_value, MarketRegion, Retailer
from NutritionService.serializers import MinorCategorySerializer, MajorCategorySerializer, HealthTippSerializer, \
    ProductSerializer, DigitalReceiptSerializer
from NutritionService.tasks import import_from_openfood

allowed_units_of_measure = ["g", "kg", "ml", "l"]


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def send_receipts_experimental(request):
    partner = request.user.partner

    if not partner:
        return Response({"error": "You must be a partner to use this API"}, status=403)

    serializer = DigitalReceiptSerializer(data=request.data)

    if serializer.is_valid():
        r2n_username = serializer.validated_data["r2n_username"]
        r2n_partner = serializer.validated_data["r2n_partner"]

        if r2n_partner != partner.name:
            # return Response({"error" : "Partner name and user mismatch"}, status = 403) need to enable in production!
            pass

        r2n_user = get_object_or_404(ReceiptToNutritionUser.objects.filter(r2n_partner__name=r2n_partner),
                                     r2n_username=r2n_username)

        if not r2n_user.r2n_user_active:
            return Response({"error": "User not active. Please check if user fulfills all relevant criteria."},
                            status=403)

        result = {"receipts": []}
        digital_receipt_list = []

        for receipt in serializer.validated_data["receipts"][:10]:

            nutri_score_array = []
            for article in receipt["items"]:
                digital_receipt = DigitalReceipt(r2n_user=r2n_user,
                                                 business_unit=receipt["business_unit"],
                                                 receipt_id=receipt["receipt_id"],
                                                 receipt_datetime=receipt["receipt_datetime"],
                                                 article_id=article["article_id"],
                                                 article_type=article["article_type"],
                                                 quantity=article["quantity"],
                                                 quantity_unit=article["quantity_unit"],
                                                 price=article["price"],
                                                 price_currency=article["price_currency"])

                digital_receipt_list.append(digital_receipt)

                product = match_receipt(digital_receipt)
                if product:
                    log_product_errors(product)
                    nutri_score = nutri_score_from_ofcom(product)
                    number_check, _ = is_number(product.product_size)
                    if product.product_size_unit_of_measure is None:
                        continue
                    try:
                        if product.product_size_unit_of_measure.lower() in ["kg", "l"]:
                            weight = float(product.product_size) * 1000  # weight in g or ml
                        else:
                            weight = float(product.product_size)

                        product_weight_in_basket = digital_receipt.quantity * weight
                        nutri_score_array.append((product_weight_in_basket, nutri_score))
                    except (TypeError, ValueError):
                        continue

            letter_nutri_score = "unknown"

            sum_product_weights = 0
            sum_product_weights_nutri_number = 0

            for t in nutri_score_array:
                try:
                    sum_product_weights_nutri_number += t[0] * t[1]
                    sum_product_weights += t[0]
                except (TypeError, ValueError):
                    continue

            if sum_product_weights > 0:
                try:
                    total_nutri_score = sum_product_weights_nutri_number / sum_product_weights
                    total_nutri_score = round(total_nutri_score, 3)

                    letter_nutri_score = __get_nutri_score_from_average(total_nutri_score)
                except (TypeError, ValueError):
                    pass

            else:
                total_nutri_score = "unknown"

            receipt_object = {
                "receipt_id": receipt["receipt_id"],
                "receipt_datetime": receipt["receipt_datetime"],
                "business_unit": receipt["business_unit"],
                "nutriscore": letter_nutri_score,
                "nutriscore_indexed": total_nutri_score,
                "r2n_version_code": 1
            }

            result["receipts"].append(receipt_object)

        for receipt in serializer.validated_data["receipts"][10:]:
            for article in receipt["items"]:
                digital_receipt = DigitalReceipt(r2n_user=r2n_user,
                                                 business_unit=receipt["business_unit"],
                                                 receipt_id=receipt["receipt_id"],
                                                 receipt_datetime=receipt["receipt_datetime"],
                                                 article_id=article["article_id"],
                                                 article_type=article["article_type"],
                                                 quantity=article["quantity"],
                                                 quantity_unit=article["quantity_unit"],
                                                 price=article["price"],
                                                 price_currency=article["price_currency"])

                digital_receipt_list.append(digital_receipt)

            receipt_object = {
                "receipt_id": receipt["receipt_id"],
                "receipt_datetime": receipt["receipt_datetime"],
                "business_unit": receipt["business_unit"],
                "nutriscore": "error: maximum amount of calls exceeded",
                "nutriscore_indexed": "error: maximum amount of calls exceeded",
                "r2n_version_code": 1
            }

            result["receipts"].append(receipt_object)

        DigitalReceipt.objects.bulk_create(digital_receipt_list)

        return Response(result, status=200)

    return Response(serializer.errors, status=400)


def match_receipt(digital_receipt):
    if digital_receipt.quantity > 0 and digital_receipt.price > 0:
        price_per_unit = digital_receipt.price / digital_receipt.quantity
    else:
        price_per_unit = digital_receipt.price

    if digital_receipt.article_type and digital_receipt.article_id:

        try:
            matched_product = Matching.objects.get(article_type=digital_receipt.article_type,
                                                   article_id=digital_receipt.article_id)

            return matched_product.eatfit_product

        except Matching.MultipleObjectsReturned:
            # If more than one matching found return randomly one for now
            # TODO return the one with the closest price
            matched_product = Matching.objects.filter(article_type=digital_receipt.article_type,
                                                      article_id=digital_receipt.article_id).first()

            return matched_product.eatfit_product

        except Matching.DoesNotExist:
            try:
                not_found_matching = NonFoundMatching.objects.get(article_id=digital_receipt.article_id,
                                                                  article_type=digital_receipt.article_type)
                not_found_matching.counter += 1
                not_found_matching.save()
            except NonFoundMatching.DoesNotExist:
                NonFoundMatching.objects.create(article_id=digital_receipt.article_id,
                                                article_type=digital_receipt.article_type,
                                                business_unit=digital_receipt.business_unit,
                                                price_per_unit=price_per_unit)
    return None


def nutri_score_from_ofcom(product):

    try:

        if product.ofcom_value is None:
            product.save()
            if product.ofcom_value is None:
                return None

        if product.major_category.pk == 20:
            return None  # product is not a food product

        if (product.major_category.pk == 1 or product.major_category.pk == 2) and \
                (not product.minor_category or product.minor_category.pk == 5 or product.minor_category.pk == 11):
            # product is a drink -> CHECK IF WATER!!!

            if product.ofcom_value <= 1:
                return 2
            elif product.ofcom_value <= 5:
                return 3
            elif product.ofcom_value <= 9:
                return 4
            else:
                return 5

        else:
            if product.ofcom_value <= -1:
                return 1
            elif product.ofcom_value <= 2:
                return 2
            elif product.ofcom_value <= 10:
                return 3
            elif product.ofcom_value <= 18:
                return 4
            else:
                return 5
    except AttributeError:
        return None

def __get_nutri_score_from_average(nutriscore_average):
    rounded_average = int(round(nutriscore_average))
    if rounded_average > 0:
        return ["A", "B", "C", "D", "E"][rounded_average - 1]
    return "A"


class ProductWeightNotANumber(Exception):
    pass


def log_product_errors(product):
    logger = logging.getLogger('NutritionService.test_product')
    product.save()

    category_check_fail = not product.major_category or not product.minor_category
    score_check_fail = not product.data_score or product.data_score < 25
    measurement_check_fail = not product.product_size_unit_of_measure or product.product_size_unit_of_measure.lower() not in allowed_units_of_measure
    product_size_check_fail = not product.product_size or product.product_size == "" or product.product_size == "0"

    is_number_check, _ = is_number(product.product_size)

    error_logs = []

    if category_check_fail:
        description = "Major or Minor Category missing: (gtin: %s)" % product.gtin
        logger.warn(description)
        error_logs.append(description)

    if score_check_fail:
        description = "Data Quality low: (gtin: %s)" % product.gtin
        logger.warn(description)
        error_logs.append(description)

    if not is_number_check:
        description = "Product's (gtin: %s) weight not a number" % product.gtin
        logger.warn(description)
        error_logs.append(description)

    if measurement_check_fail:
        description = "Product's (gtin: %s) size unit not in g, ml, L, kg" % product.gtin
        logger.warn(description)
        error_logs.append(description)

    if product_size_check_fail:
        description = "Product (gtin: %s) weight missing" % product.gtin
        logger.warn(description)
        error_logs.append(description)

    log_models = [ErrorLog(reporting_app="Eatfit_R2N",
                           gtin=product.gtin,
                           error_description=description) for description in error_logs]
    ErrorLog.objects.bulk_create(log_models)


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def send_receipts(request):
    partner = request.user.partner
    if not partner:
        return Response({"error": "You must be a partner to use this API"}, status=403)
    serializer = DigitalReceiptSerializer(data=request.data)
    if serializer.is_valid():
        r2n_username = serializer.validated_data["r2n_username"]
        r2n_partner = serializer.validated_data["r2n_partner"]
        if r2n_partner != partner.name:
            return Response({"error": "Partner name and user mismatch"}, status=403)
        r2n_user = get_object_or_404(ReceiptToNutritionUser.objects.filter(r2n_partner__name=r2n_partner),
                                     r2n_username=r2n_username)
        if not r2n_user.r2n_user_active:
            return Response({"error": "User not active. Please check if user fulfills all relevant criteria."},
                            status=403)
        receipts_calculated = 0
        result = {}
        result["receipts"] = []
        for receipt in serializer.validated_data["receipts"]:
            nutri_score_array = []
            for article in receipt["items"]:
                digital_receipt = DigitalReceipt(r2n_user=r2n_user, business_unit=receipt["business_unit"],
                                                 receipt_id=receipt["receipt_id"],
                                                 receipt_datetime=receipt["receipt_datetime"],
                                                 article_id=article["article_id"], article_type=article["article_type"],
                                                 quantity=article["quantity"], quantity_unit=article["quantity_unit"],
                                                 price=article["price"], price_currency=article["price_currency"])
                digital_receipt.save()
    return Response(status=200)


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
    products = Product.objects.filter(gtin=gtin)
    if products.exists():
        result = __prepare_product_data(request, products, False)
    else:
        products, price = __check_if_weighted_product(gtin)
        if products:
            result = __prepare_product_data(request, products, True, price)
        else:
            l, created = NotFoundLog.objects.get_or_create(gtin=gtin)
            if not created:
                l.count = l.count + 1
                l.save()
            result = {}
            result["success"] = False
            result["products"] = None
    return Response(result)

def __prepare_product_data(request, products, weighted_product, price = None):
    result_type = request.GET.get("resultType", "array")
    for product in products:
        product.found_count = product.found_count + 1
        product.save()
    serializer = ProductSerializer(products, many=True, context={'weighted_article': weighted_product, "price" : price})
    result = {}
    result["success"] = True
    if result_type == "array":
        result["products"] = serializer.data
    else:
        result["products"] = []
        for p in serializer.data:
            result["products"].append(__change_product_objects(p))
    return result


def __check_if_weighted_product(gtin):
    try:
        price_string = gtin[-5:-1]
        gtin_without_price = gtin[:-5]
        gtin_without_price = gtin_without_price + "00000"
        price_string = price_string[:2] + "." + price_string[-2:]
        price = float(price_string)
        products = Product.objects.filter(gtin=gtin_without_price)
        if products.exists():
            return products, price
    except Exception as e:
        pass
    return None, -1

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
    result_product["weighted_article"] = product["weighted_article"]
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
def get_better_products_minor_category(request, minor_category_pk):
    """
    query param: sortBy, values: 'ofcomValue', 'energyKJ', 'totalFat', 'saturatedFat', 'salt', 'sugars', 'protein',
                                 'totalCarbohydrate', 'dietaryFiber', 'healthPercentage' - this is the fruit and veg %,
                                 'sodium'
    query param: resultType, values: 'array', 'dictionary'
    """
    minor_category = get_object_or_404(MinorCategory.objects.all(), pk = minor_category_pk)
    return __get_better_products(request, minor_category, None)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_better_products_gtin(request, gtin):
    """
    query param: sortBy, values: 'ofcomValue', 'energyKJ', 'totalFat', 'saturatedFat', 'salt', 'sugars', 'protein',
                                 'totalCarbohydrate', 'dietaryFiber', 'healthPercentage' - this is the fruit and veg %,
                                 'sodium'
    query param: resultType, values: 'array', 'dictionary'
    query param: marketRegion, values: 'all', 'ch', 'de', 'au', 'fr', 'it'
    query param: retailer, values: 'all', 'migros', 'coop', 'denner', 'farmy', 'volg', 'edeka'
    """
    product = get_object_or_404(Product.objects.all(), gtin=gtin)
    return __get_better_products(request, product.minor_category, product.major_category)


def __get_better_products(request, minor_category, major_category):

    market_region_map = MarketRegion.MARKET_REGION_QUERY_MAP
    retailer_map = Retailer.RETAILER_QUERY_MAP

    sort_by = request.GET.get("sortBy", "ofcomValue")
    result_type = request.GET.get("resultType", "array")
    market_region = request.GET.get("marketRegion", "all")
    retailer = request.GET.get("retailer", "all")
    number_of_results = 20
    results_found = 0
    better_products_minor = []
    better_products_major = []
    market_region_retailer_kwargs = {}
    minor_category_kwargs = {}

    if market_region != "all":
        market_region_value = market_region_map.get(market_region, market_region)
        market_region_retailer_kwargs.update({'market_region__market_region_name': market_region_value})

    if retailer != "all":
        retailer_value = retailer_map.get(retailer, retailer)
        market_region_retailer_kwargs.update({'retailer__retailer_name': retailer_value})

    if minor_category:
        minor_category_kwargs.update({'minor_category': minor_category.pk})
        if sort_by == "ofcomValue":
            better_products_minor = Product.objects.filter(minor_category=minor_category,
                                                           **market_region_retailer_kwargs).order_by("ofcom_value")[
                                    :number_of_results]
        elif sort_by == 'healthPercentage':
            better_products_minor = Product.objects.filter(minor_category=minor_category,
                                                           **market_region_retailer_kwargs).order_by(
                "health_percentage")[:number_of_results]
        else:
            better_products_minor = Product.objects.filter(minor_category=minor_category.pk, nutrients__name=sort_by,
                                                           **market_region_retailer_kwargs).order_by(
                "nutrients__amount")[:number_of_results]
        results_found += better_products_minor.count()
        better_products_minor = list(better_products_minor)

    if results_found < number_of_results and major_category:
        if sort_by == "ofcomValue":
            better_products_major = Product.objects.filter(major_category=major_category,
                                                           **market_region_retailer_kwargs).order_by(
                "ofcom_value").exclude(**minor_category_kwargs)[
                                    :(number_of_results - results_found)]
        elif sort_by == 'healthPercentage':
            better_products_major = Product.objects.filter(major_category=major_category,
                                                           **market_region_retailer_kwargs).order_by(
                "health_percentage").exclude(**minor_category_kwargs)[:(number_of_results - results_found)]
        else:
            better_products_major = Product.objects.filter(major_category=major_category.pk, nutrients__name=sort_by,
                                                           **market_region_retailer_kwargs).order_by(
                "nutrients__amount").exclude(**minor_category_kwargs)[:(number_of_results - results_found)]
        results_found += better_products_major.count()
        better_products_major = list(better_products_major)

    products = better_products_minor + better_products_major

    if results_found > 0:
        serializer = ProductSerializer(products, many=True)
        result = {"success": True}
        if result_type == "array":
            result["products"] = serializer.data
        else:
            result["products"] = []
            for p in serializer.data:
                result["products"].append(__change_product_objects(p))
    else:
        result = {"success": False, "products": None}
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
    return Response(status = 200)

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
    data_cleaning.fill_product_names_and_images()
    return Response(status = 200)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_major_categories(request):
    categories = MajorCategory.objects.all()
    serilaizer = MajorCategorySerializer(categories, many=True)
    return Response(serilaizer.data, status = 200)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_minor_categories(request):
    categories = MinorCategory.objects.all()
    serilaizer = MinorCategorySerializer(categories, many=True)
    return Response(serilaizer.data, status = 200)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_health_tipps(request):
    request_category = request.GET.get("category", None)
    request_nutrient = request.GET.get("nutrient", None)

    if request_category and request_nutrient:
        health_tipps = HealthTipp.objects.filter(minor_categories = request_category, nutrients = request_nutrient)
    elif request_category:
        health_tipps = HealthTipp.objects.filter(minor_categories = request_category)
    elif request_nutrient:
        health_tipps = HealthTipp.objects.filter(nutrients = request_nutrient)
    else:
        return Response(status = 400)
    serializer = HealthTippSerializer(health_tipps, many=True)
    return Response(serializer.data, status = 200)

@permission_classes((permissions.IsAuthenticated,))
def export_digital_receipts(request):
    data = download_csv(request, DigitalReceipt.objects.all())
    response = HttpResponse(data, content_type='text/csv')
    filename = "export_digital_receipt_" + datetime.now().strftime("%Y_%m_%d") + ".csv"
    response['Content-Disposition'] = 'attachment;filename=' + filename
    return response

@permission_classes((permissions.IsAuthenticated,))
def export_matching(request):
    data = download_csv(request, Matching.objects.all())
    response = HttpResponse(data, content_type='text/csv')
    filename = "export_matching_" + datetime.now().strftime("%Y_%m_%d") + ".csv"
    response['Content-Disposition'] = 'attachment;filename=' + filename
    return response

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
            language_code = n['_languageCode'].lower()
            if language_code == "de":
                default_arguments["product_name_de"] = unicode(n['name'])
            if language_code == "fr":
                default_arguments["product_name_fr"] = unicode(n['name'])
            if language_code == "en":
                default_arguments["product_name_en"] = unicode(n['name'])
            if language_code == "it":
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
            if attr['_canonicalName'].startswith('allergen') and (attr['value'] == "true" or attr['value'] == 'false'):
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
    except (ValueError, TypeError):
        return False, None