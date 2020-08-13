# -*- coding: utf-8 -*-

"""
Definition of views.
"""

from __future__ import print_function, division
from datetime import datetime
import logging
from suds.client import Client
from suds.sudsobject import asdict
from toolz import itertoolz, dicttoolz

from django.db.models import F, Func
from django.http import HttpResponse
from django.http.response import HttpResponseForbidden
from django.shortcuts import get_object_or_404

from rest_framework import permissions, generics, mixins, status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response

from EatFitService.settings import TRUSTBOX_USERNAME, TRUSTBOX_PASSWORD, TRUSTBOX_URL
from NutritionService import data_cleaning, reports
from NutritionService.codecheck_integration.codecheck import import_from_codecheck
from NutritionService.helpers import store_image, download_csv, get_start_and_end_date_from_calendar_week
from NutritionService.models import DigitalReceipt, NonFoundMatching, Matching, MajorCategory, MinorCategory, \
    HealthTipp, ImportLog, Product, Allergen, NutritionFact, Ingredient, NotFoundLog, ErrorLog, \
    ReceiptToNutritionUser, calculate_ofcom_value, MarketRegion, Retailer, get_nutri_score_category, CurrentStudies, \
    NutriScoreFacts, SALT, SATURATED_FAT, SUGARS, ENERGY_KCAL, SODIUM, ENERGY_KJ
from NutritionService.nutriscore.calculations import unit_of_measure_conversion
from NutritionService.serializers import MinorCategorySerializer, MajorCategorySerializer, HealthTippSerializer, \
    ProductSerializer, DigitalReceiptSerializer, CurrentStudiesSerializer, Text2GTINSerializer
from NutritionService.tasks import import_from_openfood

from .errors import SendReceiptsErrors, BasketAnalysisErrors

logger = logging.getLogger('NutritionService.views')
allowed_units_of_measure = ["g", "kg", "ml", "l"]
NUTRI_SCORE_LETTER_TO_NUMBER_MAP = {
    'A': 4.5,
    'B': 3.5,
    'C': 2.5,
    'D': 1.5,
    'E': 0.5
}

NUTRI_SCORE_NUMBER_TO_LETTER_MAP = {
    4.5: 'A',
    3.5: 'B',
    2.5: 'C',
    1.5: 'D',
    0.5: 'E'
}
UNITS = 'units'

def nutri_score_number_to_letter(nutri_score):
    return sorted(NUTRI_SCORE_NUMBER_TO_LETTER_MAP.items(), key=lambda i: abs(i[0] - nutri_score))[0][1]

def authorize_partner(request, r2n_username, r2n_partner):
    errors = SendReceiptsErrors()

    if not hasattr(request.user, 'partner'):
        return Response({'error': errors.PARTNER_DOES_NOT_EXIST}, status=status.HTTP_403_FORBIDDEN)

    try:
        r2n_user = ReceiptToNutritionUser.objects.get(r2n_partner__name=r2n_partner, r2n_username=r2n_username)
    except ReceiptToNutritionUser.DoesNotExist:
        return Response({'error': errors.USER_NOT_FOUND}, status.HTTP_404_NOT_FOUND)

    if not r2n_user.r2n_user_active:
        return Response({'error': errors.USER_INACTIVE},
                        status=status.HTTP_403_FORBIDDEN)

    return True

class BasketDetailedAnalysisView(generics.GenericAPIView):
    pass

class BasketAnalysisView(generics.GenericAPIView):
    serializer_class = DigitalReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def validate_product(product):
        log_product_errors(product)
        size_condition, _ = is_number(product.product_size)
        unit_of_measure_condition = product.product_size_unit_of_measure is not None
        nutrients_condition = NutritionFact.objects.filter(product=product,
                                                           name__in=[SALT, SODIUM, SUGARS, SATURATED_FAT, ENERGY_KCAL,
                                                                     ENERGY_KJ]).exists()
        nutri_score_facts_condition = NutriScoreFacts.objects.filter(product=product).exists()
        if unit_of_measure_condition:
            unit_of_measure_condition = product.product_size_unit_of_measure.lower() in allowed_units_of_measure
        nutri_score_condition = product.nutri_score_final is not None

        return False not in [size_condition, unit_of_measure_condition, nutri_score_condition, nutrients_condition,
                             nutri_score_facts_condition]

    @staticmethod
    def prepare_product_nutrients_and_ofcom_values(product, size, quantity, quantity_unit):
        nutrients = list(NutritionFact.objects.filter(product=product,
                                                      name__in=[SALT, SUGARS, SATURATED_FAT, ENERGY_KCAL]))
        nutrients_grouped = itertoolz.groupby(lambda x: x.name, nutrients)
        nutri_score_facts = NutriScoreFacts.objects.get(product=product)
        minor_category = product.minor_category.id
        nutrient_potential = []
        for name, nutrient_values in nutrients_grouped.items():
            unit = None
            ofcom_value = None
            if any(nutrient.is_mixed for nutrient in nutrient_values):
                is_mixed = True
                nutrient_amount = next(nutrient.amount for nutrient in nutrient_values if nutrient.is_mixed)
            else:
                is_mixed = False
                nutrient_amount = next(nutrient.amount for nutrient in nutrient_values if nutrient.is_mixed is False)

            if quantity_unit == UNITS:
                amount = nutrient_amount * quantity
            else:
                # All nutrients per 100g/ml
                amount = (nutrient_amount * size / 100)

            if name == SALT:
                unit = 'g'
                if is_mixed:
                    ofcom_value = nutri_score_facts.ofcom_n_salt_mixed
                else:
                    ofcom_value = nutri_score_facts.ofcom_n_salt
            elif name == SUGARS:
                unit = 'g'
                if is_mixed:
                    ofcom_value = nutri_score_facts.ofcom_n_sugars_mixed
                else:
                    ofcom_value = nutri_score_facts.ofcom_n_sugars
            elif name == SATURATED_FAT:
                unit = 'g'
                if is_mixed:
                    ofcom_value = nutri_score_facts.ofcom_n_saturated_fat_mixed
                else:
                    ofcom_value = nutri_score_facts.ofcom_n_saturated_fat
            elif name == ENERGY_KCAL:
                unit = 'kcal'
                if is_mixed:
                    ofcom_value = nutri_score_facts.ofcom_n_energy_kj_mixed
                else:
                    ofcom_value = nutri_score_facts.ofcom_n_energy_kj
            else:
                continue

            nutrient_object = {'nutrient': name, 'minor_category_id': minor_category, 'product_size': size,
                               'amount': amount, 'unit': unit, 'ofcom_value': ofcom_value}
            nutrient_potential.append(nutrient_object)

        return nutrient_potential

    @staticmethod
    def calculate_nutri_score_by_basket(nutri_score_by_article):
        nutri_score_by_basket = []
        items_by_basket = itertoolz.groupby('receipt_id', nutri_score_by_article)
        for basket, items in items_by_basket.items():
            accumulated_weight = sum(item['product_weight'] for item in items)
            normalized_accumulated_nutri_score = sum(
                (item['nutri_score'] * item['product_weight']) / accumulated_weight for item in items)
            nutri_score = int(round(normalized_accumulated_nutri_score))
            nutri_score_letter = nutri_score_number_to_letter(nutri_score)
            business_unit = dicttoolz.get_in([0, 'business_unit'], items)
            date_of_purchase = dicttoolz.get_in([0, 'receipt_datetime'], items)
            nutri_score_by_basket.append({
                'receipt_id': basket,
                'receipt_datetime': date_of_purchase,
                'business_unit': business_unit,
                'nutri_score_average': nutri_score_letter,
                'nutri_score_indexed': round(normalized_accumulated_nutri_score, 2)
                })

        return nutri_score_by_basket

    @staticmethod
    def calculate_nutri_score_by_week(nutri_score_by_article):
        nutri_score_by_week = []
        items_by_year = itertoolz.groupby('year_of_receipt', nutri_score_by_article)
        for year, items in items_by_year.items():
            accumulated_weights = itertoolz.reduceby('name_of_calendar_week',
                                                     lambda acc, x: acc + x['product_weight'],
                                                     items, 0)
            accumulated_weighted_nutri_scores = itertoolz.reduceby('name_of_calendar_week',
                                                                   lambda acc, x: acc + (
                                                                               x['nutri_score'] * x['product_weight']),
                                                                   items, 0)

            normalized_accumulated_nutri_scores = dicttoolz.merge_with(lambda x: x[0] / x[1],
                                                                       accumulated_weighted_nutri_scores,
                                                                       accumulated_weights)

            for calendar_week, weighted_nutri_score in normalized_accumulated_nutri_scores.items():
                nutri_score = int(round(weighted_nutri_score))
                nutri_score_letter = nutri_score_number_to_letter(nutri_score)
                start_date, end_date = get_start_and_end_date_from_calendar_week(year, calendar_week)
                nutri_score_by_week.append({
                    'name_calendar_week': f'{year}-{calendar_week}',
                    'nutri_score_average': nutri_score_letter,
                    'nutri_score_indexed': round(weighted_nutri_score, 2),
                    'start_date': start_date,
                    'end_date': end_date
                })

        return nutri_score_by_week

    @staticmethod
    def calculate_improvement_potential(nutrient_potential):
        total_size = sum(item['product_size'] for item in nutrient_potential)
        weighted_ofcom_values_by_nutrient = itertoolz.reduceby('nutrient',
                                                               lambda acc, x: acc + x['ofcom_value'] * x[
                                                                   'product_size'] / total_size,
                                                               nutrient_potential, 0)
        total_weighted_ofcom_values = sum(weighted_ofcom_values_by_nutrient.values())
        potential_percentages_by_nutrient = dicttoolz.valmap(
            lambda x: round(x * 100 / total_weighted_ofcom_values, 2), weighted_ofcom_values_by_nutrient)
        grouped_by_nutrient = itertoolz.groupby('nutrient', nutrient_potential)

        improvement_potential = []
        for nutrient, values in grouped_by_nutrient.items():
            average_ofcom_value = sum(value['ofcom_value'] for value in values) / len(values)
            potential_percentage = potential_percentages_by_nutrient[nutrient]
            total_amount = sum(value['amount'] for value in values)
            unit = dicttoolz.get_in([0, 'unit'], values)

            amount_per_minor_category = itertoolz.reduceby('minor_category_id', lambda acc, x: acc + x['amount'],
                                                           values, 0)
            sources = [{'minor_category_id': category_id, 'amount': round(amount, 2), 'unit': unit} for
                       category_id, amount in
                       amount_per_minor_category.items()]
            sources = sorted(sources, key=lambda x: x['amount'], reverse=True)

            nutrient_potential = {
                'nutrient': nutrient,
                'ofcom_point_average': average_ofcom_value,
                'potential_percentage': potential_percentage,
                'amount': round(total_amount, 2),
                'unit': unit,
                'sources': sources
            }

            improvement_potential.append(nutrient_potential)

        return improvement_potential

    def post(self, request):
        errors = BasketAnalysisErrors()

        if not hasattr(request.user, 'partner'):
            return Response({'error': errors.PARTNER_DOES_NOT_EXIST}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        r2n_username = validated_data.get('r2n_username')
        r2n_partner = validated_data.get('r2n_partner')

        try:
            r2n_user = ReceiptToNutritionUser.objects.get(r2n_partner__name=r2n_partner, r2n_username=r2n_username)
        except ReceiptToNutritionUser.DoesNotExist:
            return Response({'error': errors.USER_NOT_FOUND}, status.HTTP_404_NOT_FOUND)

        if not r2n_user.r2n_user_active:
            return Response({'error': errors.USER_INACTIVE},
                            status=status.HTTP_403_FORBIDDEN)

        receipt_data = validated_data['receipts']
        digital_receipt_list = []
        nutri_score_by_article = []
        nutrient_potential = []

        for receipt in receipt_data:
            articles = receipt['items']
            receipt_id = receipt['receipt_id']
            receipt_datetime = receipt['receipt_datetime']
            receipt_datetime_formatted = receipt_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
            year_of_receipt = receipt_datetime.year
            calendar_week = receipt_datetime.strftime('%U')  # Assuming sunday is the first day of the week
            for article in articles:
                quantity = article['quantity']
                quantity_unit = article['quantity_unit']
                digital_receipt = DigitalReceipt(
                    r2n_user=r2n_user,
                    business_unit=receipt['business_unit'],
                    receipt_id=receipt_id,
                    receipt_datetime=receipt['receipt_datetime'],
                    article_id=article['article_id'],
                    article_type=article['article_type'],
                    quantity=quantity,
                    quantity_unit=quantity_unit,
                    price=article['price'],
                    price_currency=article['price_currency']
                )
                digital_receipt_list.append(digital_receipt)
                product = match_receipt(digital_receipt)

                if product is None:
                    continue

                if not self.validate_product(product):
                    continue

                _, product_size = is_number(product.product_size)
                unit_of_measure = product.product_size_unit_of_measure.lower()
                nutri_score_number = NUTRI_SCORE_LETTER_TO_NUMBER_MAP[product.nutri_score_final]

                if unit_of_measure == 'kg':
                    target_unit = 'g'
                elif unit_of_measure == 'l':
                    target_unit = 'ml'
                else:
                    target_unit = unit_of_measure

                product_size = unit_of_measure_conversion(product_size, unit_of_measure, target_unit)

                nutri_score_by_article.append({
                    'name_of_calendar_week': calendar_week,
                    'year_of_receipt': year_of_receipt,
                    'nutri_score': nutri_score_number,
                    'product_weight': product_size,
                    'receipt_id': receipt_id,
                    'receipt_datetime': receipt_datetime_formatted,
                    'business_unit': receipt['business_unit'],
                })
                product_nutrients_and_ofcom_values = self.prepare_product_nutrients_and_ofcom_values(product,
                                                                                                     product_size,
                                                                                                     quantity,
                                                                                                     quantity_unit)
                nutrient_potential += product_nutrients_and_ofcom_values

        nutri_score_by_basket = self.calculate_nutri_score_by_basket(nutri_score_by_article)
        nutri_score_by_week = self.calculate_nutri_score_by_week(nutri_score_by_article)
        improvement_potential = self.calculate_improvement_potential(nutrient_potential)

        result = {
            'nutri_score_by_basket': nutri_score_by_basket,
            'nutri_score_by_week': nutri_score_by_week,
            'improvement_potential': improvement_potential
        }

        DigitalReceipt.objects.bulk_create(digital_receipt_list)
        return Response(result, status=status.HTTP_200_OK)


class CurrentStudiesView(generics.ListAPIView):
    queryset = CurrentStudies.objects.all()
    serializer_class = CurrentStudiesSerializer
    permission_classes = [permissions.IsAuthenticated]

class SendReceiptsGetProductIdsView(generics.GenericAPIView):
    def post(self, request):
        errors = SendReceiptsErrors()

        if not hasattr(request.user, 'partner'):
            return Response({'error': errors.PARTNER_DOES_NOT_EXIST}, status=status.HTTP_403_FORBIDDEN)

        serializer = Text2GTINSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        r2n_username = validated_data.get('r2n_username')
        r2n_partner = validated_data.get('r2n_partner')

        try:
            r2n_user = ReceiptToNutritionUser.objects.get(r2n_partner__name=r2n_partner, r2n_username=r2n_username)
        except ReceiptToNutritionUser.DoesNotExist:
            return Response({'error': errors.USER_NOT_FOUND}, status.HTTP_404_NOT_FOUND)

        if not r2n_user.r2n_user_active:
            return Response({'error': errors.USER_INACTIVE},
                            status=status.HTTP_403_FORBIDDEN)

        products = []
        for article in validated_data['articles']:
            digital_receipt = DigitalReceipt(
                r2n_user=r2n_user,
                article_id=article['article_id'],
                article_type=article['article_type'],
                quantity=article['quantity'],
                quantity_unit=article['quantity_unit'],
                price=article['price'],
                price_currency=article['price_currency']
            )
            product = match_receipt(digital_receipt)
            if product:
                products.append({
                    "article_id": article['article_id'],
                    "article_type": article['article_type'],
                    "eatfit_id": product.id,
                    "gtin": product.gtin,
                })

        return Response(products, status=status.HTTP_200_OK)


class SendReceiptsView(generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = DigitalReceipt.objects.all()
    serializer_class = DigitalReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def product_is_valid(product):
        log_product_errors(product)
        size_condition, _ = is_number(product.product_size)
        unit_of_measure_condition = product.product_size_unit_of_measure is not None
        if unit_of_measure_condition:
            unit_of_measure_condition = product.product_size_unit_of_measure.lower() in allowed_units_of_measure
        nutri_score_condition = product.nutri_score_final is not None

        return False not in [size_condition, unit_of_measure_condition, nutri_score_condition]

    def post(self, request):
        MAXIMUM_RECEIPTS = 12  #  Maximum number of baskets which should be processed
        VERSION = 2  # Current Version of API

        errors = SendReceiptsErrors()

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        r2n_username = validated_data.get('r2n_username')
        r2n_partner = validated_data.get('r2n_partner')

        validation = authorize_partner(request, r2n_username, r2n_partner)
        if isinstance(validation, Response):
            return validation

        r2n_user = ReceiptToNutritionUser.objects.get(r2n_partner__name=r2n_partner, r2n_username=r2n_username)

        receipt_data = validated_data['receipts']
        digital_receipt_list = []
        result = {'receipts': []}

        for receipt in receipt_data[:MAXIMUM_RECEIPTS]:
            nutri_scores = []
            product_weights_sum = 0
            articles = receipt['items']
            for article in articles:
                digital_receipt = DigitalReceipt(
                    r2n_user=r2n_user,
                    business_unit=receipt['business_unit'],
                    receipt_id=receipt['receipt_id'],
                    receipt_datetime=receipt['receipt_datetime'],
                    article_id=article['article_id'],
                    article_type=article['article_type'],
                    quantity=article['quantity'],
                    quantity_unit=article['quantity_unit'],
                    price=article['price'],
                    price_currency=article['price_currency']
                )
                digital_receipt_list.append(digital_receipt)
                product = match_receipt(digital_receipt)

                if product is None:
                    continue

                if article['quantity_unit'] in ['unit', 'units']:
                    # Calculate units
                    # Check if we have all the information to calculate nutri score:
                    if not is_number(product.product_size):
                        continue

                    weight = float(product.product_size)
                    if product.product_size_unit_of_measure.lower() in ["kg", "l"]:
                        weight = float(product.product_size) * 1000  # weight in g or ml

                    product_weight_in_basket = digital_receipt.quantity * weight
                elif article['quantity_unit'] in ['kg', 'g', 'l', 'ml']:
                    # Calculate with weight
                    weight = float(article['quantity'])
                    if article['quantity_unit'] in ["kg", "l"]:
                        weight = float(article['quantity']) * 1000  # weight in g or ml


                    product_weight_in_basket = weight
                else:
                    continue

                nutri_score_number = NUTRI_SCORE_LETTER_TO_NUMBER_MAP[product.nutri_score_final]

                nutri_scores.append(nutri_score_number * product_weight_in_basket)
                product_weights_sum += product_weight_in_basket


            if not nutri_scores or product_weights_sum == 0:
                total_nutri_score_raw = errors.UNKNOWN
                total_nutri_score_letter = errors.UNKNOWN
            else:
                total_nutri_score_raw = sum(nutri_scores) / product_weights_sum
                total_nutri_score_letter = nutri_score_number_to_letter(total_nutri_score_raw)
                total_nutri_score_raw = round(total_nutri_score_raw, 9)


            receipt_object = {
                'receipt_id': receipt['receipt_id'],
                'receipt_datetime': receipt['receipt_datetime'],
                'business_unit': receipt['business_unit'],
                'nutriscore': total_nutri_score_letter,
                'nutriscore_indexed': total_nutri_score_raw,
                'r2n_version_code': VERSION
            }
            result['receipts'].append(receipt_object)

        for receipt in receipt_data[MAXIMUM_RECEIPTS:]:
            articles = receipt['items']
            for article in articles:
                digital_receipt = DigitalReceipt(
                    r2n_user=r2n_user,
                    business_unit=receipt['business_unit'],
                    receipt_id=receipt['receipt_id'],
                    receipt_datetime=receipt['receipt_datetime'],
                    article_id=article['article_id'],
                    article_type=article['article_type'],
                    quantity=article['quantity'],
                    quantity_unit=article['quantity_unit'],
                    price=article['price'],
                    price_currency=article['price_currency']
                )
                digital_receipt_list.append(digital_receipt)
                receipt_object = {
                    'receipt_id': receipt['receipt_id'],
                    'receipt_datetime': receipt['receipt_datetime'],
                    'business_unit': receipt['business_unit'],
                    'nutriscore': errors.MAXIMUM_REACHED,
                    'nutriscore_indexed': errors.MAXIMUM_REACHED,
                    'r2n_version_code': VERSION
                }
                result['receipts'].append(receipt_object)

        DigitalReceipt.objects.bulk_create(digital_receipt_list)
        return Response(result, status=status.HTTP_200_OK)


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

        for receipt in serializer.validated_data["receipts"][:12]:

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

        for receipt in serializer.validated_data["receipts"][12:]:
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
            matched_product = Matching.objects.filter(article_type=digital_receipt.article_type,
                                                      article_id=digital_receipt.article_id,
                                                      price_per_unit__isnull=False).annotate(
                absolute_price_difference=Func(F('price_per_unit') - price_per_unit, function='ABS')).order_by(
                'absolute_price_difference').first()

            if matched_product is None:
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
    products = Product.objects.filter(gtin=gtin)\
        .select_related('nutri_score_facts')\
        .prefetch_related('ingredients', 'nutrients')
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


def __prepare_product_data(request, products, weighted_product, price=None):
    result_type = request.GET.get("resultType", "array")
    products.update(found_count=F('found_count') + 1)
    for product in products:
        # If nutriscore has not been calculated, calculate it
        if not product.nutri_score_final:
            logger.info('Product gtin=%s has no nutriscore. Calculating now.' % product.gtin)
            product.save()
    serializer = ProductSerializer(products, many=True, context={'weighted_article': weighted_product, "price": price})
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
        result_product["nutrients"][n["name"]]["unit_of_measure"] = n["unit_of_measure"]
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
    minor_category = get_object_or_404(MinorCategory.objects.all(), pk=minor_category_pk)
    return __get_better_products(request, minor_category, None)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_worse_products_minor_category(request, minor_category_pk):
    """
    query param: sortBy, values: 'ofcomValue', 'energyKJ', 'totalFat', 'saturatedFat', 'salt', 'sugars', 'protein',
                                 'totalCarbohydrate', 'dietaryFiber', 'healthPercentage' - this is the fruit and veg %,
                                 'sodium'
    query param: resultType, values: 'array', 'dictionary'
    """
    minor_category = get_object_or_404(MinorCategory.objects.all(), pk=minor_category_pk)
    return __get_worse_products(request, minor_category, None)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_worse_products_gtin(request, gtin):
    """
    query param: sortBy, values: 'ofcomValue', 'energyKJ', 'totalFat', 'saturatedFat', 'salt', 'sugars', 'protein',
                                 'totalCarbohydrate', 'dietaryFiber', 'healthPercentage' - this is the fruit and veg %,
                                 'sodium'
    query param: resultType, values: 'array', 'dictionary'
    query param: marketRegion, values: 'ch', 'de', 'au', 'fr', 'it'
    query param: retailer, values: 'migros', 'coop', 'denner', 'farmy', 'volg', 'edeka'
    """
    product = get_object_or_404(Product.objects.all(), gtin=gtin)
    return __get_worse_products(request, product.minor_category, product.major_category)


def __get_worse_products(request, minor_category, major_category):
    sort_by = request.GET.get("sortBy", "ofcomValue")
    result_type = request.GET.get("resultType", "array")
    market_region = request.GET.get("marketRegion", None)
    retailer = request.GET.get("retailer", None)
    number_of_results = 20

    better_products_query = _get_better_products_query(minor_category, major_category, market_region, retailer,
                                                       number_of_results)

    if sort_by == 'ofcomValue':
        better_products_query = better_products_query.order_by('-ofcom_value')
    elif sort_by == 'healthPercentage':
        better_products_query = better_products_query.order_by('-health_percentage')
    else:
        better_products_query = better_products_query.filter(nutrients__name=sort_by).order_by('-nutrients__amount')

    results_found = better_products_query.count()

    products = list(better_products_query[:number_of_results])

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
def get_better_products_gtin(request, gtin):
    """
    query param: sortBy, values: 'ofcomValue', 'energyKJ', 'totalFat', 'saturatedFat', 'salt', 'sugars', 'protein',
                                 'totalCarbohydrate', 'dietaryFiber', 'healthPercentage' - this is the fruit and veg %,
                                 'sodium'
    query param: resultType, values: 'array', 'dictionary'
    query param: marketRegion, values: 'ch', 'de', 'au', 'fr', 'it'
    query param: retailer, values: 'migros', 'coop', 'denner', 'farmy', 'volg', 'edeka'
    """
    product = get_object_or_404(Product.objects.all(), gtin=gtin)
    return __get_better_products(request, product.minor_category, product.major_category)


def __get_better_products(request, minor_category, major_category):
    sort_by = request.GET.get("sortBy", "ofcomValue")
    result_type = request.GET.get("resultType", "array")
    market_region = request.GET.get("marketRegion", None)
    retailer = request.GET.get("retailer", None)
    number_of_results = 20

    better_products_query = _get_better_products_query(minor_category, major_category, market_region, retailer, number_of_results)
    
    if sort_by == 'ofcomValue':
        better_products_query = better_products_query.order_by('ofcom_value')
    elif sort_by == 'healthPercentage':
        better_products_query = better_products_query.order_by('health_percentage')
    else:
        better_products_query = better_products_query.filter(nutrients__name=sort_by).order_by('nutrients__amount')

    results_found = better_products_query.count()

    products = list(better_products_query[:number_of_results])

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

def _get_better_products_query(minor_category, major_category, market_region, retailer, number_of_results):
    better_products_query = Product.objects.prefetch_related('nutrients', 'market_region', 'retailer')
    results_found = 0

    market_region_map = MarketRegion.MARKET_REGION_QUERY_MAP
    if market_region:
        market_region = market_region.lower()
        market_region_value = market_region_map.get(market_region, market_region)
        better_products_query = better_products_query.filter(
            market_region__market_region_name__iexact=market_region_value
        )

    if retailer:
        retailer = retailer.lower()
        better_products_query = better_products_query.filter(retailer__retailer_name__iexact=retailer)

    if minor_category:
        better_products_query = better_products_query.filter(minor_category=minor_category)
        results_found = better_products_query.count()

    if results_found < number_of_results and major_category:
        better_products_query = better_products_query.filter(major_category=major_category)

    better_products_query = better_products_query.exclude(nutri_score_final__isnull=True)
    return better_products_query


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def update_database(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    """ checks for changes since last update and adds new objects"""
    last_updated = '2000-01-01T00:00:00Z'
    import_log_queryset = ImportLog.objects.filter(import_finished__isnull=False).order_by("-import_finished")[:1]
    if import_log_queryset.exists():
        last_updated = import_log_queryset[0].import_finished.strftime("%Y-%m-%dT%H:%M:%SZ")
    __update_objects_from_trustbox(last_updated)
    return HttpResponse(status=200)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_products_from_openfood(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    import_from_openfood()
    return HttpResponse(status=200)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_products_from_codecheck(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    import_from_codecheck()
    return Response(status=200)


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
    return Response(status=200)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def generate_status_report(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    reports.generate_daily_report()
    return Response(status=200)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def data_clean_task(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    data_cleaning.clean_salt_sodium()
    data_cleaning.fill_product_names_and_images()
    return Response(status=200)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_major_categories(request):
    categories = MajorCategory.objects.all()
    serilaizer = MajorCategorySerializer(categories, many=True)
    return Response(serilaizer.data, status=200)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_minor_categories(request):
    categories = MinorCategory.objects.all()
    serilaizer = MinorCategorySerializer(categories, many=True)
    return Response(serilaizer.data, status=200)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_health_tipps(request):
    request_category = request.GET.get("category", None)
    request_nutrient = request.GET.get("nutrient", None)

    if request_category and request_nutrient:
        health_tipps = HealthTipp.objects.filter(minor_categories=request_category, nutrients=request_nutrient)
    elif request_category:
        health_tipps = HealthTipp.objects.filter(minor_categories=request_category)
    elif request_nutrient:
        health_tipps = HealthTipp.objects.filter(nutrients=request_nutrient)
    else:
        return Response(status=400)
    serializer = HealthTippSerializer(health_tipps, many=True)
    return Response(serializer.data, status=200)


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
    import_log = ImportLog.objects.create(import_started=datetime.now())
    count = 0
    for gtin in updated_gtins:
        count += 1
        result = client.service.getTrustedDataByGTIN(gtin, TRUSTBOX_USERNAME, TRUSTBOX_PASSWORD)
        __soap_response_to_objects(result)
        logger.debug("imported model: " + str(count))
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
        # Check if product is flagged for automatic updates
        automated_update_flag_off = Product.objects.filter(gtin=p["_gtin"],
                                                           automatic_update=False).exists()
        if automated_update_flag_off:
            return

        default_arguments = {}
        temp_image_url = None
        for n in p['productNames']:
            language_code = n['_languageCode'].lower()
            if language_code == "de":
                default_arguments["product_name_de"] = str(n['name'])
            if language_code == "fr":
                default_arguments["product_name_fr"] = str(n['name'])
            if language_code == "en":
                default_arguments["product_name_en"] = str(n['name'])
            if language_code == "it":
                default_arguments["product_name_it"] = str(n['name'])
        for attr in p['productAttributes']:
            try:
                if attr['_canonicalName'] == 'manufacturer':
                    default_arguments["producer"] = str(attr['value'])
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
                    # check against 0 due to multiple entries with different values
                    default_arguments["serving_size"] = attr['value']
        default_arguments["source"] = Product.TRUSTBOX
        default_arguments["source_checked"] = True
        product, created = Product.objects.update_or_create(gtin=p['_gtin'], defaults=default_arguments)
        if temp_image_url:
            store_image(temp_image_url, product)

        # create nutrition facts for products
        if 'nutritionFacts' in p['nutrition']['nutritionFactsGroups']:
            for attr in p['nutrition']['nutritionFactsGroups']['nutritionFacts']:
                try:
                    is_a_number, number = is_number(attr['amount'])
                    base_unit_of_measure_condition = attr['_baseUnitOfMeasure'] == 'g'
                    base_amount_condition = attr['_baseAmount'] == '100'
                    if is_a_number and base_unit_of_measure_condition and base_amount_condition:
                        default_arguments = {"amount": number, "unit_of_measure": attr['unitOfMeasure']}
                        NutritionFact.objects.update_or_create(product=product, name=attr["_canonicalName"],
                                                               defaults=default_arguments)
                except (ValueError, TypeError, KeyError):  # ignore poor data quality
                    continue

        # create allergens and ingridients for products
        for attr in p['nutrition']['nutritionAttributes']:
            if attr['_canonicalName'].startswith('allergen') and (attr['value'] == "true" or attr['value'] == 'false'):
                Allergen.objects.update_or_create(product=product, name=attr["_canonicalName"],
                                                  defaults={"certainity": attr['value']})
            if attr['_canonicalName'] == 'ingredients':
                Ingredient.objects.update_or_create(product=product, lang=attr["_languageCode"],
                                                    defaults={"text": str(attr['value'])})
        calculate_ofcom_value(product)
    except Exception as e:
        print(e)


def is_number(s):
    try:
        v = float(s)
        return True, v
    except (ValueError, TypeError):
        return False, None
