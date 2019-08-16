from model_mommy import mommy
import itertools
import pytest

from NutritionService.models import Product, NutritionFact


@pytest.mark.django_db(transaction=True)
def test_data_sufficiency():
    """
    The purpose of this test is to ensure that insufficient data should return a Nutriscore-value (ofcom) of 0.
    Case 1: The value associated with a NutritionFact field is not convertible to a float -> Ofcom = 0
    Case 2: There is no unit of measure specified for sodium (g or mg) -> Ofcom = 0
    Case 3: Sufficient data has been provided for calculating a score -> Ofcom = n
    """
    test_prod = mommy.make(Product)

    try:
        test_nutrients = {'name': 'saturatedFat', 'amount': 'Twelve point four', 'unit_of_measure': '',
                          'is_mixed': False}
        test_prod.nutrients.create(**test_nutrients)
        test_prod.save()
    except ValueError:
        assert test_prod.ofcom_value == 0

    test_nutrients = {'name': 'sodium', 'amount': 12.4, 'unit_of_measure': '', 'is_mixed': False}
    test_prod.nutrients.create(**test_nutrients)
    test_prod.save()

    assert test_prod.ofcom_value == 0

    test_prod = mommy.make(Product)
    test_nutrients = {'name': 'sugars', 'amount': 50, 'unit_of_measure': 'g', 'is_mixed': False}
    test_prod.nutrients.create(**test_nutrients)
    test_prod.save()

    assert test_prod.ofcom_value == 10  # 50 > argmax([values]) = 45


@pytest.mark.django_db
def test_sodium():

    test_prod = mommy.make(Product)

    test_nutrients = {'name': 'sodium', 'amount': 1.2, 'unit_of_measure': 'g', 'is_mixed': False}
    test_prod.nutrients.create(**test_nutrients)
    test_prod.save()

    nutri_score_1 = test_prod.ofcom_value
    assert nutri_score_1 == 10

    test_nutrients = {'name': 'sodium', 'amount': 270, 'unit_of_measure': 'mg', 'is_mixed': False}
    test_prod.nutrients.update(**test_nutrients)
    test_prod.save()

    nutri_score_2 = test_prod.ofcom_value
    assert nutri_score_2 == 2
    assert nutri_score_1 != nutri_score_2


@pytest.mark.django_db
def test_mixed():

    test_prod = mommy.make(Product)

    mixed = {'name': 'protein', 'amount': 10, 'unit_of_measure': 'g', 'is_mixed': True}
    not_mixed = {'name': 'protein', 'amount': 1.5, 'unit_of_measure': 'g', 'is_mixed': False}

    mommy.make(NutritionFact, product=test_prod, **mixed)
    mommy.make(NutritionFact, product=test_prod, **not_mixed)

    test_prod.save()
    assert test_prod.ofcom_value == -5
