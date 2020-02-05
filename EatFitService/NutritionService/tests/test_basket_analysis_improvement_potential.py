import pytest
from model_mommy import mommy

from NutritionService.nutriscore.calculations import unit_of_measure_conversion
from NutritionService.views import views
from NutritionService import models


@pytest.mark.django_db
def test_basket_analysis_improvement_potential_is_valid():
    assert models.MajorCategory.objects.count() == 0
    assert models.MinorCategory.objects.count() == 0
    assert models.Product.objects.count() == 0
    assert models.NutritionFact.objects.count() == 0

    major_category = mommy.make(models.MajorCategory, pk=16)
    minor_category = mommy.make(models.MinorCategory, pk=82, category_major=major_category,
                                nutri_score_category=models.FOOD)

    test_product = mommy.make(models.Product, minor_category=minor_category, product_size='1',
                              product_size_unit_of_measure='l')
    mommy.make(models.NutritionFact, product=test_product, name='saturatedFat', amount=5.3, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=test_product, name='energyKcal', amount=280.2, unit_of_measure='kcal')
    mommy.make(models.NutritionFact, product=test_product, name='energyKJ', amount=500, unit_of_measure='kj')
    mommy.make(models.NutritionFact, product=test_product, name='sugars', amount=11.6, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=test_product, name='dietaryFiber', amount=2.1, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=test_product, name='protein', amount=7.4, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=test_product, name='sodium', amount=300, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=test_product, name='salt', amount=620, unit_of_measure='g')

    assert models.MajorCategory.objects.count() == 1
    assert models.MinorCategory.objects.count() == 1
    assert models.Product.objects.count() == 1
    assert models.NutritionFact.objects.count() == 8

    test_product.save()

    _, product_size = views.is_number(test_product.product_size)
    unit_of_measure = test_product.product_size_unit_of_measure.lower()

    if unit_of_measure == 'kg':
        target_unit = 'g'
    elif unit_of_measure == 'l':
        target_unit = 'ml'
    else:
        target_unit = unit_of_measure

    product_size = unit_of_measure_conversion(product_size, unit_of_measure, target_unit)
    basket_analysis_api_test_instance = views.BasketAnalysisView()

    assert basket_analysis_api_test_instance.validate_product(test_product)

    nutrient_potential = basket_analysis_api_test_instance.prepare_product_nutrients_and_ofcom_values(test_product,
                                                                                                      product_size, 1,
                                                                                                      'units')
    results = basket_analysis_api_test_instance.calculate_improvement_potential(nutrient_potential)
    expected_results = [
        {'nutrient': 'saturatedFat', 'ofcom_point_average': 5.0, 'potential_percentage': 27.78, 'amount': 5.3,
         'unit': 'g', 'sources': [{'minor_category_id': 82, 'amount': 5.3, 'unit': 'g'}]},
        {'nutrient': 'energyKcal', 'ofcom_point_average': 1.0, 'potential_percentage': 5.56, 'amount': 280.2,
         'unit': 'kcal', 'sources': [{'minor_category_id': 82, 'amount': 280.2, 'unit': 'kcal'}]},
        {'nutrient': 'sugars', 'ofcom_point_average': 2.0, 'potential_percentage': 11.11, 'amount': 11.6,
         'unit': 'g', 'sources': [{'minor_category_id': 82, 'amount': 11.6, 'unit': 'g'}]},
        {'nutrient': 'salt', 'ofcom_point_average': 10.0, 'potential_percentage': 55.56, 'amount': 620.0,
         'unit': 'g', 'sources': [{'minor_category_id': 82, 'amount': 620.0, 'unit': 'g'}]}]

    assert results == expected_results
