import json
from model_mommy import mommy
import pytest
from toolz import itertoolz

from NutritionService.models import Product, NutritionFact, Ingredient, Allergen
from NutritionService.views.views import create_product

with open('NutritionService/tests/trustbox_import_data/trusted_data.json', 'r') as infile:
    product = json.load(infile)


@pytest.mark.django_db
def test_trustbox_import_create():

    assert Product.objects.count() == 0

    product_processed = product['productList'][0]['products'][0]
    create_product(product_processed)

    assert Product.objects.count() == 1


@pytest.mark.django_db
def test_trustbox_import_automatic_update_off():

    assert Product.objects.count() == 0

    mommy.make(Product, gtin=7610032043383, automatic_update=False)

    assert Product.objects.count() == 1

    product_processed = product['productList'][0]['products'][0]
    create_product(product_processed)

    assert Product.objects.count() == 1

    test_product = Product.objects.get(gtin=7610032043383)

    assert not test_product.product_name_de
    assert not test_product.product_name_fr
    assert not test_product.product_name_it
    assert not test_product.product_name_en
    assert not test_product.producer
    assert not test_product.product_size
    assert not test_product.product_size_unit_of_measure
    assert not test_product.source
    assert not test_product.source_checked
    assert NutritionFact.objects.count() == 0
    assert Ingredient.objects.count() == 0
    assert Allergen.objects.count() == 0


@pytest.mark.django_db
def test_trustbox_import_automatic_update_on():

    assert Product.objects.count() == 0

    mommy.make(Product, gtin=7610032043383, automatic_update=True)

    product_processed = product['productList'][0]['products'][0]
    create_product(product_processed)

    assert Product.objects.count() == 1

    test_product = Product.objects.get(gtin=7610032043383)

    assert test_product.product_name_de == 'DAR-VIDA Choco noir 4PP 184g'
    assert test_product.product_name_fr == 'DAR-VIDA Choco noir 4PP 184g'
    assert test_product.product_name_it == 'DAR-VIDA Choco noir 4PP 184g'
    assert test_product.product_name_en == 'DAR-VIDA Choco noir 4PP 184g'
    assert test_product.producer == 'HUG AG'
    assert test_product.product_size == '0.184'
    assert test_product.product_size_unit_of_measure == 'kg'
    assert test_product.source == 'Trustbox'
    assert test_product.source_checked
    assert NutritionFact.objects.count() == 3
    assert Ingredient.objects.count() == 4
    assert Allergen.objects.count() == 5


@pytest.mark.django_db
def test_trustbox_import_base_unit_of_measurement_base_amount():
    """
    We want to assert that _baseUnitofMeasure and _baseAmount follow a specific pattern (g/100) when creating or
    updating data from the Trustbox importer. All data with the name "energyKcal in the testing data do not follow the
    required pattern, therefore it should be ignored and not present in the testing database.
    """

    assert Product.objects.count() == 0

    mommy.make(Product, gtin=7610032043383, automatic_update=True)

    product_processed = product['productList'][0]['products'][0]
    create_product(product_processed)

    nutrition_fact_objects = NutritionFact.objects.all()
    nutrition_fact_objects_grouped_name = itertoolz.groupby(lambda x: x.name, list(nutrition_fact_objects))

    assert Product.objects.count() == 1
    assert NutritionFact.objects.count() == 3
    assert 'energyKcal' not in nutrition_fact_objects_grouped_name  # _baseUnitofMeasure and _baseAmount not g/100


@pytest.mark.django_db
def test_trustbox_import_exceptions():
    """
    Test cases:
    1) protein: amount = "seven point seven" cannot be converted to float (ValueError)
    2) totalFat:  amount = None cannot be converted to float (TypeError)
    3) energyKJ: _baseUnitofMeasure and _baseAmount keys not present in the data (KeyError)
    4) saturatedFat: unitOfMeausre key not present in the data (KeyError)
    5) sugars: _canonicalName key not present in the data (KeyError)
    """

    assert Product.objects.count() == 0

    mommy.make(Product, gtin=7610032043383, automatic_update=True)

    product_processed = product['productList'][0]['products'][0]
    create_product(product_processed)

    nutrition_fact_objects = NutritionFact.objects.all()
    nutrition_fact_objects_grouped_name = itertoolz.groupby(lambda x: x.name, list(nutrition_fact_objects))

    assert Product.objects.count() == 1
    assert NutritionFact.objects.count() == 3
    assert 'protein' not in nutrition_fact_objects_grouped_name
    assert 'totalFat' not in nutrition_fact_objects_grouped_name
    assert 'energyKJ' not in nutrition_fact_objects_grouped_name
    assert 'saturatedFat' not in nutrition_fact_objects_grouped_name
    assert 'sugars' not in nutrition_fact_objects_grouped_name
