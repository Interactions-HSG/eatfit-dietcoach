import pytest
from model_mommy import mommy

from NutritionService.views import views
from NutritionService import models


@pytest.mark.django_db
@pytest.mark.xfail(raises=AssertionError)
def test_basket_analysis_product_is_mineral_water():
    assert models.MajorCategory.objects.count() == 0
    assert models.MinorCategory.objects.count() == 0
    assert models.Product.objects.count() == 0
    assert models.NutritionFact.objects.count() == 0

    major_category = mommy.make(models.MajorCategory, pk=16)
    minor_category = mommy.make(models.MinorCategory, pk=82, category_major=major_category,
                                nutri_score_category=models.MINERAL_WATER)

    test_product = mommy.make(models.Product, minor_category=minor_category, product_size='1',
                              product_size_unit_of_measure='l')
    mommy.make(models.NutritionFact, product=test_product, name='saturatedFat', amount=5.3, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=test_product, name='energyKcal', amount=280.2, unit_of_measure='kcal')
    mommy.make(models.NutritionFact, product=test_product, name='energyKJ', amount=500, unit_of_measure='kj')
    mommy.make(models.NutritionFact, product=test_product, name='sugars', amount=11.6, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=test_product, name='dietaryFiber', amount=2.1, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=test_product, name='protein', amount=7.4, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=test_product, name='sodium', amount=620, unit_of_measure='mg')

    assert models.MajorCategory.objects.count() == 1
    assert models.MinorCategory.objects.count() == 1
    assert models.Product.objects.count() == 1
    assert models.NutritionFact.objects.count() == 7

    test_product.save()
    basket_analysis_api_test_instance = views.BasketAnalysisView()

    assert basket_analysis_api_test_instance.validate_product(test_product) is False


@pytest.mark.django_db
def test_basket_analysis_product_is_valid():
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
    mommy.make(models.NutritionFact, product=test_product, name='sodium', amount=620, unit_of_measure='mg')

    assert models.MajorCategory.objects.count() == 1
    assert models.MinorCategory.objects.count() == 1
    assert models.Product.objects.count() == 1
    assert models.NutritionFact.objects.count() == 7

    test_product.save()
    basket_analysis_api_test_instance = views.BasketAnalysisView()

    assert basket_analysis_api_test_instance.validate_product(test_product)
