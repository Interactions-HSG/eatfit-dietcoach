import pytest
from model_mommy import mommy
import datetime

from NutritionService.nutriscore.calculations import unit_of_measure_conversion
from NutritionService.views import views
from NutritionService import models
from NutritionService.helpers import get_start_and_end_date_from_calendar_week

@pytest.mark.django_db
def test_basket_analysis_nutri_score_by_week_is_valid():
    assert models.MajorCategory.objects.count() == 0
    assert models.MinorCategory.objects.count() == 0
    assert models.Product.objects.count() == 0
    assert models.NutritionFact.objects.count() == 0

    major_category = mommy.make(models.MajorCategory, pk=16)
    minor_category = mommy.make(models.MinorCategory, pk=82, category_major=major_category,
                                nutri_score_category=models.FOOD)

    test_product = mommy.make(models.Product, minor_category=minor_category, product_size='100',
                              product_size_unit_of_measure='g')
    mommy.make(models.NutritionFact, product=test_product, name='saturatedFat', amount=5.3, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=test_product, name='energyKcal', amount=280.2, unit_of_measure='kcal')
    mommy.make(models.NutritionFact, product=test_product, name='energyKJ', amount=500, unit_of_measure='kj')
    mommy.make(models.NutritionFact, product=test_product, name='sugars', amount=11.6, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=test_product, name='dietaryFiber', amount=2.1, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=test_product, name='protein', amount=7.4, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=test_product, name='sodium', amount=620, unit_of_measure='mg')
    mommy.make(models.NutritionFact, product=test_product, name='salt', amount=620, unit_of_measure='mg')

    assert models.MajorCategory.objects.count() == 1
    assert models.MinorCategory.objects.count() == 1
    assert models.Product.objects.count() == 1
    assert models.NutritionFact.objects.count() == 8

    test_product.save()

    _, product_size = views.is_number(test_product.product_size)
    unit_of_measure = test_product.product_size_unit_of_measure.lower()
    nutri_score_number = views.NUTRI_SCORE_LETTER_TO_NUMBER_MAP[test_product.nutri_score_final]

    if unit_of_measure == 'kg':
        target_unit = 'g'
    elif unit_of_measure == 'l':
        target_unit = 'ml'
    else:
        target_unit = unit_of_measure

    product_size = unit_of_measure_conversion(product_size, unit_of_measure, target_unit)

    basket_analysis_api_test_instance = views.BasketAnalysisView()
    receipt_datetime = datetime.datetime.now()
    receipt_datetime_formatted = receipt_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
    year_of_receipt = receipt_datetime.year
    calendar_week = receipt_datetime.strftime('%U')
    start_date, end_date = get_start_and_end_date_from_calendar_week(year_of_receipt, calendar_week)

    weighted_nutri_score_by_calendar_week = [{'name_of_calendar_week': calendar_week,
                                              'year_of_receipt': year_of_receipt,
                                              'nutri_score': nutri_score_number,
                                              'product_weight': product_size,
                                              'receipt_id': '000-1-A',
                                              'receipt_datetime': receipt_datetime_formatted,
                                              'business_unit': 'Coop'}]

    assert basket_analysis_api_test_instance.validate_product(test_product)

    results = basket_analysis_api_test_instance.calculate_nutri_score_by_week(weighted_nutri_score_by_calendar_week)
    expected_results = [{'name_calendar_week': f'{year_of_receipt}-{calendar_week}',
                         'nutri_score_average': test_product.nutri_score_final,
                         'nutri_score_indexed': views.NUTRI_SCORE_LETTER_TO_NUMBER_MAP[test_product.nutri_score_final],
                         'start_date': start_date,
                         'end_date': end_date,
                         }]

    assert results == expected_results
