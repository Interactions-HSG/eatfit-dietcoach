import json
from model_mommy import mommy
import pytest

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
    assert NutritionFact.objects.count() == 9
    assert Ingredient.objects.count() == 4
    assert Allergen.objects.count() == 5
