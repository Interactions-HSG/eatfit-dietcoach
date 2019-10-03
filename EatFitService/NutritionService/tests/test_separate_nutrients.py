from model_mommy import mommy
import pytest

from NutritionService.models import ErrorLog, Product, NutritionFact, get_and_validate_nutrients, separate_nutrients


@pytest.mark.django_db
def test_nutrient_separation():
    """
    Test cases:
    1) Nutrients are correctly separated into mixed and non-mixed nutrients
    """
    assert Product.objects.count() == 0
    assert NutritionFact.objects.count() == 0

    test_product = mommy.make(Product)
    mommy.make(NutritionFact, product=test_product, name='protein', amount=0.7, unit_of_measure='g', is_mixed=True)
    mommy.make(NutritionFact, product=test_product, name='protein', amount=1.0, unit_of_measure='g', is_mixed=False)

    assert Product.objects.count() == 1
    assert NutritionFact.objects.count() == 2

    validated_nutrients = get_and_validate_nutrients(test_product)

    assert ErrorLog.objects.count() == 0
    assert len(validated_nutrients) == 2

    mixed, not_mixed = separate_nutrients(validated_nutrients, test_product.gtin)

    assert ErrorLog.objects.count() == 0
    assert len(mixed) == 1
    assert len(not_mixed) == 1

    test_nutrient_mixed = mixed[0]

    assert test_nutrient_mixed.name == 'protein'
    assert test_nutrient_mixed.amount == 0.7
    assert test_nutrient_mixed.unit_of_measure == 'g'
    assert test_nutrient_mixed.is_mixed

    test_nutrient_not_mixed = not_mixed[0]

    assert test_nutrient_not_mixed.name == 'protein'
    assert test_nutrient_not_mixed.amount == 1.0
    assert test_nutrient_not_mixed.unit_of_measure == 'g'
    assert not test_nutrient_not_mixed.is_mixed


@pytest.mark.django_db
def test_nutrient_reduction():
    """
    Test cases:
    1) Nutrients are correctly separated into mixed and non-mixed nutrients
    2) Last nutrient was selected when multiple entries were found for the same nutrient name
    """
    assert Product.objects.count() == 0
    assert NutritionFact.objects.count() == 0

    test_product = mommy.make(Product)
    mommy.make(NutritionFact, product=test_product, name='protein', amount=0.7, unit_of_measure='g', is_mixed=True)
    mommy.make(NutritionFact, product=test_product, name='protein', amount=0.8, unit_of_measure='g', is_mixed=True)
    mommy.make(NutritionFact, product=test_product, name='protein', amount=0.9, unit_of_measure='g', is_mixed=True)
    mommy.make(NutritionFact, product=test_product, name='protein', amount=1.0, unit_of_measure='g', is_mixed=False)
    mommy.make(NutritionFact, product=test_product, name='protein', amount=2.0, unit_of_measure='g', is_mixed=False)
    mommy.make(NutritionFact, product=test_product, name='protein', amount=3.0, unit_of_measure='g', is_mixed=False)

    assert Product.objects.count() == 1
    assert NutritionFact.objects.count() == 6

    validated_nutrients = get_and_validate_nutrients(test_product)

    assert ErrorLog.objects.count() == 0
    assert len(validated_nutrients) == 6

    mixed, not_mixed = separate_nutrients(validated_nutrients, test_product.gtin)

    assert ErrorLog.objects.count() == 2
    assert len(mixed) == 1
    assert len(not_mixed) == 1

    test_nutrient_mixed = mixed[0]

    assert test_nutrient_mixed.name == 'protein'
    assert test_nutrient_mixed.amount == 0.9
    assert test_nutrient_mixed.unit_of_measure == 'g'
    assert test_nutrient_mixed.is_mixed

    test_nutrient_not_mixed = not_mixed[0]

    assert test_nutrient_not_mixed.name == 'protein'
    assert test_nutrient_not_mixed.amount == 3.0
    assert test_nutrient_not_mixed.unit_of_measure == 'g'
    assert not test_nutrient_not_mixed.is_mixed
