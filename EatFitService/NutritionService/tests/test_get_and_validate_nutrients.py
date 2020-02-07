from model_mommy import mommy
import pytest

from NutritionService.models import MINERAL_WATER, MajorCategory, MinorCategory, ErrorLog, Product, NutritionFact, \
    get_and_validate_nutrients
from NutritionService.nutriscore.calculations import unit_of_measure_conversion


@pytest.mark.django_db
def test_nutri_score_nutrient_name():
    """
    Test cases:
    1) Nutrient does not have a name
    2) Nutrient does not have a valid name
    3) Nutrient name is correct
    """
    assert MajorCategory.objects.count() == 0
    assert MinorCategory.objects.count() == 0
    assert Product.objects.count() == 0
    assert NutritionFact.objects.count() == 0

    major_category = mommy.make(MajorCategory, pk=16)
    minor_category = mommy.make(MinorCategory, pk=82, category_major=major_category, nutri_score_category=MINERAL_WATER)

    test_product = mommy.make(Product, minor_category=minor_category)
    mommy.make(NutritionFact, product=test_product, name=None, amount=1.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='randomName', amount=1.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='protein', amount=1.0, unit_of_measure='g')

    assert MajorCategory.objects.count() == 1
    assert MinorCategory.objects.count() == 1
    assert Product.objects.count() == 1
    assert NutritionFact.objects.count() == 3
    assert ErrorLog.objects.count() == 0

    validated_nutrients = get_and_validate_nutrients(test_product)

    assert ErrorLog.objects.count() == 0
    assert len(validated_nutrients) == 1


@pytest.mark.django_db
def test_nutri_score_nutrient_amount():
    """
    Test cases:
    1) Nutrient amount = None cannot be converted to float (TypeError)
    2) Nutrient amount = 1.1 is valid
    """
    assert MajorCategory.objects.count() == 0
    assert MinorCategory.objects.count() == 0
    assert Product.objects.count() == 0
    assert NutritionFact.objects.count() == 0

    major_category = mommy.make(MajorCategory, pk=16)
    minor_category = mommy.make(MinorCategory, pk=82, category_major=major_category, nutri_score_category=MINERAL_WATER)

    test_product = mommy.make(Product, minor_category=minor_category)
    mommy.make(NutritionFact, product=test_product, name='protein', amount=None, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='sugars', amount=1.1, unit_of_measure='g')

    assert Product.objects.count() == 1
    assert NutritionFact.objects.count() == 2
    assert ErrorLog.objects.count() == 0

    validated_nutrients = get_and_validate_nutrients(test_product)

    assert ErrorLog.objects.count() == 1
    assert len(validated_nutrients) == 1


@pytest.mark.django_db
def test_salt_sodium_conversion():
    assert MajorCategory.objects.count() == 0
    assert MinorCategory.objects.count() == 0
    assert Product.objects.count() == 0
    assert NutritionFact.objects.count() == 0

    major_category = mommy.make(MajorCategory, pk=16)
    minor_category = mommy.make(MinorCategory, pk=82, category_major=major_category, nutri_score_category=MINERAL_WATER)

    test_product = mommy.make(Product, minor_category=minor_category)
    mommy.make(NutritionFact, product=test_product, name='salt', amount=5, unit_of_measure='mg')
    mommy.make(NutritionFact, product=test_product, name='saturatedFat', amount=1.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='sugars', amount=1.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='energyKJ', amount=125.0, unit_of_measure='kcal')

    assert Product.objects.count() == 1
    assert NutritionFact.objects.count() == 4
    assert ErrorLog.objects.count() == 0

    validated_nutrients = get_and_validate_nutrients(test_product)

    assert ErrorLog.objects.count() == 0
    assert len(validated_nutrients) == 4

    nutrient_sodium_amount = next(nutrient.amount for nutrient in validated_nutrients if nutrient.name == 'sodium')
    assert nutrient_sodium_amount == 2.0


def test_unit_of_measure_conversion():
    """
    Test cases:
    All pair combinations of kg, g, mg, l, dl, cl, ml
    """
    test_amount = 1.0
    kg = 'kg'
    l = 'l'
    cl = 'cl'
    dl = 'dl'
    g = 'g'
    ml = 'ml'
    mg = 'mg'

    # Kilogram

    kg_to_kg = unit_of_measure_conversion(test_amount, kg, kg)
    kg_to_g = unit_of_measure_conversion(test_amount, kg, g)
    kg_to_mg = unit_of_measure_conversion(test_amount, kg, mg)
    kg_to_l = unit_of_measure_conversion(test_amount, kg, l)
    kg_to_cl = unit_of_measure_conversion(test_amount, kg, cl)
    kg_to_dl = unit_of_measure_conversion(test_amount, kg, dl)
    kg_to_ml = unit_of_measure_conversion(test_amount, kg, ml)

    assert kg_to_kg == 1.0
    assert kg_to_g == 1000.0
    assert kg_to_mg == 1000000.0
    assert kg_to_l == 1.0
    assert kg_to_dl == 10.0
    assert kg_to_cl == 100.0
    assert kg_to_ml == 1000.0

    # Gram

    g_to_kg = unit_of_measure_conversion(test_amount, g, kg)
    g_to_g = unit_of_measure_conversion(test_amount, g, g)
    g_to_mg = unit_of_measure_conversion(test_amount, g, mg)
    g_to_l = unit_of_measure_conversion(test_amount, g, l)
    g_to_dl = unit_of_measure_conversion(test_amount, g, dl)
    g_to_cl = unit_of_measure_conversion(test_amount, g, cl)
    g_to_ml = unit_of_measure_conversion(test_amount, g, ml)

    assert g_to_kg == 0.001
    assert g_to_g == 1.0
    assert g_to_mg == 1000.0
    assert g_to_l == 0.001
    assert g_to_dl == 0.01
    assert g_to_cl == 0.1
    assert g_to_ml == 1.0

    # Milligram

    mg_to_kg = unit_of_measure_conversion(test_amount, mg, kg)
    mg_to_g = unit_of_measure_conversion(test_amount, mg, g)
    mg_to_mg = unit_of_measure_conversion(test_amount, mg, mg)
    mg_to_l = unit_of_measure_conversion(test_amount, mg, l)
    mg_to_dl = unit_of_measure_conversion(test_amount, mg, dl)
    mg_to_cl = unit_of_measure_conversion(test_amount, mg, cl)
    mg_to_ml = unit_of_measure_conversion(test_amount, mg, ml)

    assert mg_to_kg == 10**-6
    assert mg_to_g == 0.001
    assert mg_to_mg == 1.0
    assert mg_to_l == 10**-6
    assert mg_to_dl == 10**-5
    assert mg_to_cl == 0.0001
    assert mg_to_ml == 0.001

    # Liter
    
    l_to_kg = unit_of_measure_conversion(test_amount, l, kg)
    l_to_g = unit_of_measure_conversion(test_amount, l, g)
    l_to_mg = unit_of_measure_conversion(test_amount, l, mg)
    l_to_l = unit_of_measure_conversion(test_amount, l, l)
    l_to_dl = unit_of_measure_conversion(test_amount, l, dl)
    l_to_cl = unit_of_measure_conversion(test_amount, l, cl)
    l_to_ml = unit_of_measure_conversion(test_amount, l, ml)

    assert l_to_kg == 1.0
    assert l_to_g == 1000.0
    assert l_to_mg == 1000000.0
    assert l_to_l == 1.0
    assert l_to_dl == 10.0
    assert l_to_cl == 100.0
    assert l_to_ml == 1000.0

    # Deciliter

    dl_to_kg = unit_of_measure_conversion(test_amount, dl, kg)
    dl_to_g = unit_of_measure_conversion(test_amount, dl, g)
    dl_to_mg = unit_of_measure_conversion(test_amount, dl, mg)
    dl_to_l = unit_of_measure_conversion(test_amount, dl, l)
    dl_to_dl = unit_of_measure_conversion(test_amount, dl, dl)
    dl_to_cl = unit_of_measure_conversion(test_amount, dl, cl)
    dl_to_ml = unit_of_measure_conversion(test_amount, dl, ml)

    assert dl_to_kg == 0.1
    assert dl_to_g == 100.0
    assert dl_to_mg == 100000.0
    assert dl_to_l == 0.1
    assert dl_to_dl == 1.0
    assert dl_to_cl == 10.0
    assert dl_to_ml == 100.0

    # Centiliter

    cl_to_kg = unit_of_measure_conversion(test_amount, cl, kg)
    cl_to_g = unit_of_measure_conversion(test_amount, cl, g)
    cl_to_mg = unit_of_measure_conversion(test_amount, cl, mg)
    cl_to_l = unit_of_measure_conversion(test_amount, cl, l)
    cl_to_dl = unit_of_measure_conversion(test_amount, cl, dl)
    cl_to_cl = unit_of_measure_conversion(test_amount, cl, cl)
    cl_to_ml = unit_of_measure_conversion(test_amount, cl, ml)

    assert cl_to_kg == 0.01
    assert cl_to_g == 10.0
    assert cl_to_mg == 10000.0
    assert cl_to_l == 0.01
    assert cl_to_dl == 0.1
    assert cl_to_cl == 1.0
    assert cl_to_ml == 10.0

    # Milliliter

    ml_to_kg = unit_of_measure_conversion(test_amount, ml, kg)
    ml_to_g = unit_of_measure_conversion(test_amount, ml, g)
    ml_to_mg = unit_of_measure_conversion(test_amount, ml, mg)
    ml_to_l = unit_of_measure_conversion(test_amount, ml, l)
    ml_to_dl = unit_of_measure_conversion(test_amount, ml, dl)
    ml_to_cl = unit_of_measure_conversion(test_amount, ml, cl)
    ml_to_ml = unit_of_measure_conversion(test_amount, ml, ml)

    assert ml_to_kg == 0.001
    assert ml_to_g == 1.0
    assert ml_to_mg == 1000.0
    assert ml_to_l == 0.001
    assert ml_to_dl == 0.01
    assert ml_to_cl == 0.1
    assert ml_to_ml == 1.0


@pytest.mark.xfail
def test_nutri_score_conversion_error():
    """
    Test cases:
    1) TypeError: magnitude parameter is None or not a float or integer
    2) AttributeError: target_unit data type is None
    3) UndefinedUnitError: target_unit parameter is not defined as unit of measurement
    4) DimensionalityError: current_unit parameter does not share context with target_unit
    """
    unit_of_measure_conversion(None, 'g', 'g')
    unit_of_measure_conversion('One', 'g', 'g')
    unit_of_measure_conversion(b'1', 'g', 'g')
    unit_of_measure_conversion(1, 'g', 'g')
    unit_of_measure_conversion(1.0, 'g', None)
    unit_of_measure_conversion(1.0, 'g', 'lalala')
    unit_of_measure_conversion(1.0, None, 'g')
    unit_of_measure_conversion(1.0, 'lalala', 'g')


@pytest.mark.django_db
def test_nutri_score_unit_of_measure_conversion():
    """
    Test cases:
    1) DimensionalityError: current_unit parameter does not share context with target_unit ('m')
    2) UndefinedUnitError: current_unit or target_unit parameter is not defined as unit of measurement ('lalala')
    3) Nutrient unit of measure is valid
    """
    assert Product.objects.count() == 0
    assert NutritionFact.objects.count() == 0

    test_product = mommy.make(Product)
    mommy.make(NutritionFact, product=test_product, name='saturatedFat', amount=1.0, unit_of_measure='m')
    mommy.make(NutritionFact, product=test_product, name='sugars', amount=1.0, unit_of_measure='lalala')
    mommy.make(NutritionFact, product=test_product, name='sodium', amount=1.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='energyKJ', amount=125.0, unit_of_measure='kcal')

    assert Product.objects.count() == 1
    assert NutritionFact.objects.count() == 4

    validated_nutrients = get_and_validate_nutrients(test_product)

    assert ErrorLog.objects.count() == 3
    assert len(validated_nutrients) == 2

    test_nutrient_sodium = validated_nutrients[0]

    assert test_nutrient_sodium.amount == 1000.0
    assert test_nutrient_sodium.unit_of_measure == 'mg'

    test_nutrient_energy = validated_nutrients[1]

    assert test_nutrient_energy.amount == 523.0
    assert test_nutrient_energy.unit_of_measure == 'kj'
