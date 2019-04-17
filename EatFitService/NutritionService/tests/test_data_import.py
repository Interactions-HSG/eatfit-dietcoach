# -*- coding: utf-8 -*-

from __future__ import print_function
from model_mommy import mommy
import pytest
import requests_mock

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from django.contrib.auth.models import User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory

from NutritionService.data_import import ImportBase, AllergensImport
from NutritionService.forms import AllergensForm, NutrientsForm, ProductsForm
from NutritionService.models import Product, Allergen, NutritionFact, MajorCategory, MinorCategory, ImportErrorLog, \
     Ingredient, AdditionalImage, Retailer, MarketRegion
from NutritionService.views.utils_view import AllergensView, NutrientsView, ProductsView


@pytest.mark.django_db
@pytest.mark.parametrize('url', [
    reverse('tools'),
    reverse('import-allergens'),
    reverse('import-nutrients'),
    reverse('import-products'),
])
def test_is_authenticated(url):
    client = APIClient()
    response = client.post(url, {})

    assert '/accounts/login' in response.url
    assert response.status_code == 302


@pytest.mark.django_db
def test_allergens_form():
    with open('NutritionService/tests/allergens_test.csv') as infile:
        allergens_csv_file = SimpleUploadedFile(infile.name, infile.read())

    allergens_fields = {'allergen_name': 'Update',
                        'allergen_certainty': 'None'}
    allergens_file = {'file': allergens_csv_file}
    allergens_form = AllergensForm(allergens_fields, allergens_file)

    assert allergens_form.is_valid()


@pytest.mark.django_db
def test_nutrients_form():
    with open('NutritionService/tests/nutrients_test.csv') as infile:
        nutrients_csv_file = SimpleUploadedFile(infile.name, infile.read())

    nutrients_fields = {'nutrients_name': 'Update',
                        'nutrients_amount': 'Create',
                        'nutrients_unit_of_measure': 'None'}
    nutrients_file = {'file': nutrients_csv_file}
    nutrients_form = NutrientsForm(nutrients_fields, nutrients_file)

    assert nutrients_form.is_valid()


@pytest.mark.django_db
def test_products_form():
    with open('NutritionService/tests/products_test.csv') as infile:
        products_csv_file = SimpleUploadedFile(infile.name, infile.read())

    products_fields = {'product_name_de': 'Update',
                       'product_name_en': 'Create',
                       'product_name_fr': 'None',
                       'product_name_it': 'Create',
                       'product_image': 'Update',
                       'product_ingredients': 'None',
                       'product_major': 'Update',
                       'product_minor': 'None',
                       'product_weight_unit': 'None',
                       'product_weight_integer': 'Create',
                       'product_retailer': 'Update',
                       'product_market_region': 'None'}
    products_file = {'file': products_csv_file}
    products_form = ProductsForm(products_fields, products_file)

    assert products_form.is_valid()


@pytest.mark.django_db
def test_encoding():
    form_data = {'allergen_name': 'Update',
                 'allergen_certainty': 'None'}

    bad_file_path = 'NutritionService/tests/badfile_test.csv'
    bad_test = AllergensImport(bad_file_path, form_data)

    good_file_path = 'NutritionService/tests/allergens_test.csv'
    good_test = AllergensImport(good_file_path, form_data)

    assert not bad_test.check_encoding()
    assert good_test.check_encoding()


@pytest.mark.django_db
def test_headers():
    allergen_data = {'allergen_name': 'Update',
                     'allergen_certainty': 'None'}

    bad_file_path = 'NutritionService/tests/nutrients_test.csv'
    bad_test = AllergensImport(bad_file_path, allergen_data)

    good_file_path = 'NutritionService/tests/allergens_test.csv'
    good_test = AllergensImport(good_file_path, allergen_data)

    assert not bad_test.check_headers()
    assert good_test.check_headers()


@pytest.mark.django_db
def test_emails_sent():
    assert len(mail.outbox) == 0

    importer = ImportBase(None, None)
    importer.execute_import()

    assert len(mail.outbox) == 2


def create_user():
    user = User.objects.create_user(username='test', password='test')
    return user


@pytest.mark.django_db
def test_allergen_import_update():

    test_prod = mommy.make(Product, gtin=5000159431668)
    test_allergens = {'name': 'allergenSoy', 'certainity': 'false'}
    test_prod.allergens.update(**test_allergens)

    factory = RequestFactory()

    with open('NutritionService/tests/allergens_test.csv') as infile:
        allergens_csv_file = SimpleUploadedFile(infile.name, infile.read())

    form_data = {'allergen_name': 'Update',
                 'allergen_certainty': 'Update',
                 'file': allergens_csv_file}

    request = factory.post('/tools/import-allergens/', form_data)
    request.user = create_user()
    view = AllergensView.as_view()
    response = view(request)

    assert response.status_code == 302
    assert test_prod.allergens.filter(name='allergenMilk', certainity='true').exists()


@pytest.mark.django_db
def test_allergen_import_create():
    test_prod = mommy.make(Product, gtin=5000159431668)
    test_allergens = {'name': 'allergenSoy', 'certainity': 'false'}
    test_prod.allergens.update(**test_allergens)

    factory = RequestFactory()

    with open('NutritionService/tests/allergens_test.csv') as infile:
        allergens_csv_file = SimpleUploadedFile(infile.name, infile.read())

    form_data = {'allergen_name': 'Create',
                 'allergen_certainty': 'Create',
                 'file': allergens_csv_file}

    request = factory.post('/tools/import-allergens/', form_data)
    request.user = create_user()
    view = AllergensView.as_view()
    response = view(request)

    assert response.status_code == 302
    assert not test_prod.allergens.filter(name='allergenMilk', certainity='true').exists()


@pytest.mark.django_db
def test_allergen_import_error_logging():
    assert ImportErrorLog.objects.count() == 0
    assert Allergen.objects.count() == 0

    mommy.make(Product, gtin=5000159431668)

    factory = RequestFactory()

    with open('NutritionService/tests/allergens_test.csv') as infile:
        allergens_csv_file = SimpleUploadedFile(infile.name, infile.read())

    form_data = {'allergen_name': 'Update',
                 'allergen_certainty': 'Create',
                 'file': allergens_csv_file}

    request = factory.post('/tools/import-allergens/', form_data)
    request.user = create_user()
    view = AllergensView.as_view()
    response = view(request)

    assert response.status_code == 302
    assert Allergen.objects.count() == 1
    assert ImportErrorLog.objects.count() == 29


@pytest.mark.django_db
def test_nutrient_import_update():

    test_prod = mommy.make(Product, gtin=9011900196084)
    test_nutrients = {'name': 'saturated_fat', 'amount': 12.4, 'unit_of_measure': 'hl'}
    test_prod.nutrients.update(**test_nutrients)

    factory = RequestFactory()

    with open('NutritionService/tests/nutrients_test.csv') as infile:
        nutrients_csv_file = SimpleUploadedFile(infile.name, infile.read())

    form_data = {'nutrients_name': 'Update',
                 'nutrients_amount': 'Update',
                 'nutrients_unit_of_measure': 'Update',
                 'file': nutrients_csv_file}

    request = factory.post('/tools/import-nutrients/', form_data)
    request.user = create_user()
    view = NutrientsView.as_view()
    response = view(request)

    assert response.status_code == 302
    assert test_prod.nutrients.filter(name='protein', amount=0.7, unit_of_measure='g').exists()


@pytest.mark.django_db
def test_nutrient_import_create():

    test_prod = mommy.make(Product, gtin=9011900196084)
    test_nutrients = {'name': 'saturated_fat', 'amount': 12.4, 'unit_of_measure': 'hl'}
    test_prod.nutrients.update(**test_nutrients)

    factory = RequestFactory()

    with open('NutritionService/tests/nutrients_test.csv') as infile:
        nutrients_csv_file = SimpleUploadedFile(infile.name, infile.read())

    form_data = {'nutrients_name': 'Create',
                 'nutrients_amount': 'Create',
                 'nutrients_unit_of_measure': 'Create',
                 'file': nutrients_csv_file}

    request = factory.post('/tools/import-nutrients/', form_data)
    request.user = create_user()
    view = NutrientsView.as_view()
    response = view(request)

    assert response.status_code == 302
    assert not test_prod.nutrients.filter(name='protein', amount=0.7, unit_of_measure='g').exists()


@pytest.mark.django_db
def test_nutrient_import_error_logging():
    assert ImportErrorLog.objects.count() == 0
    assert NutritionFact.objects.count() == 0

    test_prod = mommy.make(Product, gtin=9011900196084)
    test_nutrients = {'name': 'saturated_fat', 'amount': 12.4, 'unit_of_measure': 'hl'}
    test_prod.nutrients.update(**test_nutrients)

    factory = RequestFactory()

    with open('NutritionService/tests/nutrients_test.csv') as infile:
        nutrients_csv_file = SimpleUploadedFile(infile.name, infile.read())

    form_data = {'nutrients_name': 'Update',
                 'nutrients_amount': 'Update',
                 'nutrients_unit_of_measure': 'Update',
                 'file': nutrients_csv_file}

    request = factory.post('/tools/import-nutrients/', form_data)
    request.user = create_user()
    view = NutrientsView.as_view()
    response = view(request)

    assert response.status_code == 302
    assert NutritionFact.objects.count() == 1
    assert ImportErrorLog.objects.count() == 29


@pytest.mark.django_db
@pytest.mark.xfail(raises=Product.DoesNotExist)
def test_product_on_pk():
    """
    We want to assert that the ID from the CSV-file is not being set as primary key
        of the Product object in the database.
    We test this by setting the ID from the first entry in the file as query parameter
        and by trying to retrieve the object from the database with it.
    """

    factory = RequestFactory()

    with open('NutritionService/tests/products_test.csv') as infile:
        product_csv_file = SimpleUploadedFile(infile.name, infile.read())

    form_data = {'product_name_de': 'Update',
                 'product_name_en': 'None',
                 'product_name_fr': 'None',
                 'product_name_it': 'None',
                 'product_image': 'None',
                 'product_ingredients': 'None',
                 'product_major': 'None',
                 'product_minor': 'None',
                 'product_weight_unit': 'Update',
                 'product_weight_integer': 'Update',
                 'product_retailer': 'None',
                 'product_market_region': 'None',
                 'file': product_csv_file}

    request = factory.post('/tools/import-products/', form_data)
    request.user = create_user()
    view = ProductsView.as_view()
    response = view(request)

    assert response.status_code == 302
    assert Product.objects.count() == 30

    Product.objects.get(id=543070)


@pytest.mark.django_db
def test_product_import_safe_update_and_create():
    mommy.make(Product, gtin=4009233003433, product_name_de='Erster Fall', product_name_en='First Case',
               product_size_unit_of_measure='stone', product_size='17')

    factory = RequestFactory()

    with open('NutritionService/tests/products_test.csv') as infile:
        product_csv_file = SimpleUploadedFile(infile.name, infile.read())

    form_data = {'product_name_de': 'Update',
                 'product_name_en': 'Create',
                 'product_name_fr': 'None',
                 'product_name_it': 'None',
                 'product_image': 'None',
                 'product_ingredients': 'None',
                 'product_major': 'None',
                 'product_minor': 'None',
                 'product_weight_unit': 'Update',
                 'product_weight_integer': 'Update',
                 'product_retailer': 'None',
                 'product_market_region': 'None',
                 'file': product_csv_file}

    request = factory.post('/tools/import-products/', form_data)
    request.user = create_user()
    view = ProductsView.as_view()
    response = view(request)

    assert response.status_code == 302
    assert Product.objects.count() == 30
    assert Product.objects.filter(gtin=4009233003433, product_name_de='Original Wagner Steinofen Vegetaria',
                                  product_name_en='First Case', product_size_unit_of_measure='g',
                                  product_size='370').exists()


@pytest.mark.django_db
def test_product_import_ingredients_update():

    test_prod = mommy.make(Product, gtin=4009233003433)
    test_ingredients = {'text': 'alles', 'lang': 'FI'}
    test_prod.ingredients.update(**test_ingredients)

    factory = RequestFactory()

    with open('NutritionService/tests/products_test.csv') as infile:
        product_csv_file = SimpleUploadedFile(infile.name, infile.read())

    form_data = {'product_name_de': 'None',
                 'product_name_en': 'None',
                 'product_name_fr': 'None',
                 'product_name_it': 'None',
                 'product_image': 'None',
                 'product_ingredients': 'Update',
                 'product_major': 'None',
                 'product_minor': 'None',
                 'product_weight_unit': 'None',
                 'product_weight_integer': 'None',
                 'product_retailer': 'None',
                 'product_market_region': 'None',
                 'file': product_csv_file}

    request = factory.post('/tools/import-products/', form_data)
    request.user = create_user()
    view = ProductsView.as_view()
    response = view(request)

    test_string = 'WEIZENMEHL, Paprika, Zucchini, Zwiebeln, Oliven, Peperonischoten, Branntweinessig, Speisesalz, Citronensäure, Ascorbinsäure, Tomaten (23%), schnittfester Mozzarella (13%), Wasser, pflanzliches Öl (Raps), Wasser, Olivenöl, Hefe, jodiertes Speisesalz, Zucker, VOLLMILCHPULVER, Zwiebeln, Kräuter und Gewürze, Knoblauch, Pflanzenmargarine (Palmfett, Kokosfett), Mono-und Diglyceride von Speisefettsäuren, Citronensäure, weißer Balsamico Essig (Weißweinessig, Traubenmost) Die Inhaltsstoffe sind gemäß Deklarationspflicht absteigend nach der Menge zu ordnen.'

    assert response.status_code == 302
    assert Product.objects.count() == 30
    assert test_prod.ingredients.filter(text=test_string, lang='de').exists()


@pytest.mark.django_db
def test_product_import_ingredients_create():

    test_prod = mommy.make(Product, gtin=4009233003433)
    test_ingredients = {'text': 'alles', 'lang': 'FI'}
    test_prod.ingredients.update(**test_ingredients)

    factory = RequestFactory()

    with open('NutritionService/tests/products_test.csv') as infile:
        product_csv_file = SimpleUploadedFile(infile.name, infile.read())

    form_data = {'product_name_de': 'None',
                 'product_name_en': 'None',
                 'product_name_fr': 'None',
                 'product_name_it': 'None',
                 'product_image': 'None',
                 'product_ingredients': 'Create',
                 'product_major': 'None',
                 'product_minor': 'None',
                 'product_weight_unit': 'None',
                 'product_weight_integer': 'None',
                 'product_retailer': 'None',
                 'product_market_region': 'None',
                 'file': product_csv_file}

    request = factory.post('/tools/import-products/', form_data)
    request.user = create_user()
    view = ProductsView.as_view()
    response = view(request)

    test_string_fail = 'WEIZENMEHL, Paprika, Zucchini, Zwiebeln, Oliven, Peperonischoten, Branntweinessig, Speisesalz, Citronensäure, Ascorbinsäure, Tomaten (23%), schnittfester Mozzarella (13%), Wasser, pflanzliches Öl (Raps), Wasser, Olivenöl, Hefe, jodiertes Speisesalz, Zucker, VOLLMILCHPULVER, Zwiebeln, Kräuter und Gewürze, Knoblauch, Pflanzenmargarine (Palmfett, Kokosfett), Mono-und Diglyceride von Speisefettsäuren, Citronensäure, weißer Balsamico Essig (Weißweinessig, Traubenmost) Die Inhaltsstoffe sind gemäß Deklarationspflicht absteigend nach der Menge zu ordnen.'

    assert response.status_code == 302
    assert Product.objects.count() == 30
    assert not test_prod.ingredients.filter(text=test_string_fail, lang='de').exists()


@pytest.mark.django_db
@requests_mock.Mocker()
def test_product_import_load_main_image(mock):
    with open('NutritionService/tests/product_image.jpg') as infile:
        test_img = infile.read()

    mock.get(requests_mock.ANY, content=test_img)

    factory = RequestFactory()

    with open('NutritionService/tests/products_test.csv') as infile:
        product_csv_file = SimpleUploadedFile(infile.name, infile.read())

    form_data = {'product_name_de': 'None',
                 'product_name_en': 'None',
                 'product_name_fr': 'None',
                 'product_name_it': 'None',
                 'product_image': 'Update',
                 'product_ingredients': 'None',
                 'product_major': 'None',
                 'product_minor': 'None',
                 'product_weight_unit': 'None',
                 'product_weight_integer': 'None',
                 'product_retailer': 'None',
                 'product_market_region': 'None',
                 'file': product_csv_file}

    request = factory.post('/tools/import-products/', form_data)
    request.user = create_user()
    view = ProductsView.as_view()
    response = view(request)

    assert response.status_code == 302
    assert Product.objects.count() == 30
    assert Product.objects.filter(image__isnull=False).count() == 30


@pytest.mark.django_db
@requests_mock.Mocker()
def test_product_import_main_image_exists_update(mock):
    with open('NutritionService/tests/product_image.jpg') as infile:
        test_img = infile.read()

    mock.get(requests_mock.ANY, content=test_img)

    test_prod = mommy.make(Product, gtin=4018852104216, original_image_url='https://www.example.com/')

    with open('NutritionService/tests/product_image.jpg') as infile:
        product_main_image = SimpleUploadedFile(infile.name, infile.read())

    test_prod.image = product_main_image
    test_prod.save()

    factory = RequestFactory()

    with open('NutritionService/tests/products_test.csv') as infile:
        product_csv_file = SimpleUploadedFile(infile.name, infile.read())

    form_data = {'product_name_de': 'None',
                 'product_name_en': 'None',
                 'product_name_fr': 'None',
                 'product_name_it': 'None',
                 'product_image': 'Update',
                 'product_ingredients': 'None',
                 'product_major': 'None',
                 'product_minor': 'None',
                 'product_weight_unit': 'None',
                 'product_weight_integer': 'None',
                 'product_retailer': 'None',
                 'product_market_region': 'None',
                 'file': product_csv_file}

    request = factory.post('/tools/import-products/', form_data)
    request.user = create_user()
    view = ProductsView.as_view()
    response = view(request)

    assert response.status_code == 302
    assert Product.objects.count() == 30
    assert Product.objects.filter(image__isnull=False).count() == 30
    assert AdditionalImage.objects.count() == 1


@pytest.mark.django_db
def test_product_import_major_category():
    test_cat = MajorCategory.objects.create(id=10, name_de='Hallo')
    test_prod = mommy.make(Product, gtin=4009233003433, major_category=test_cat)

    assert test_prod.major_category is not None

    new_cat = MajorCategory.objects.create(id=12, name_de='Welt')

    factory = RequestFactory()

    with open('NutritionService/tests/products_test.csv') as infile:
        product_csv_file = SimpleUploadedFile(infile.name, infile.read())

    form_data = {'product_name_de': 'None',
                 'product_name_en': 'None',
                 'product_name_fr': 'None',
                 'product_name_it': 'None',
                 'product_image': 'None',
                 'product_ingredients': 'None',
                 'product_major': 'Update',
                 'product_minor': 'None',
                 'product_weight_unit': 'None',
                 'product_weight_integer': 'None',
                 'product_retailer': 'None',
                 'product_market_region': 'None',
                 'file': product_csv_file}

    request = factory.post('/tools/import-products/', form_data)
    request.user = create_user()
    view = ProductsView.as_view()
    response = view(request)

    assert response.status_code == 302
    assert Product.objects.count() == 30
    assert Product.objects.filter(gtin=4009233003433, major_category=new_cat).exists()


@pytest.mark.django_db
def test_product_import_minor_category():
    test_cat = MinorCategory.objects.create(id=50, name_de='Freundlicher Gruss')
    test_prod = mommy.make(Product, gtin=4009233003433, minor_category=test_cat)

    assert test_prod.minor_category is not None

    new_cat = MinorCategory.objects.create(id=56, name_de='Umher')

    factory = RequestFactory()

    with open('NutritionService/tests/products_test.csv') as infile:
        product_csv_file = SimpleUploadedFile(infile.name, infile.read())

    form_data = {'product_name_de': 'None',
                 'product_name_en': 'None',
                 'product_name_fr': 'None',
                 'product_name_it': 'None',
                 'product_image': 'None',
                 'product_ingredients': 'None',
                 'product_major': 'None',
                 'product_minor': 'Update',
                 'product_weight_unit': 'None',
                 'product_weight_integer': 'None',
                 'product_retailer': 'None',
                 'product_market_region': 'None',
                 'file': product_csv_file}

    request = factory.post('/tools/import-products/', form_data)
    request.user = create_user()
    view = ProductsView.as_view()
    response = view(request)

    assert response.status_code == 302
    assert Product.objects.count() == 30
    assert Product.objects.filter(gtin=4009233003433, minor_category=new_cat).exists()


@pytest.mark.django_db
def test_product_import_retailer_update():
    update_retailer_prod = mommy.make(Product, gtin=4009233003433)
    retailer = {'retailer_name': 'null'}
    update_retailer_prod.retailer.update(**retailer)

    create_retailer_prod = mommy.make(Product, gtin=9002233011953)

    factory = RequestFactory()

    with open('NutritionService/tests/products_test.csv') as infile:
        product_csv_file = SimpleUploadedFile(infile.name, infile.read())

    form_data = {'product_name_de': 'None',
                 'product_name_en': 'None',
                 'product_name_fr': 'None',
                 'product_name_it': 'None',
                 'product_image': 'None',
                 'product_ingredients': 'None',
                 'product_major': 'None',
                 'product_minor': 'None',
                 'product_weight_unit': 'None',
                 'product_weight_integer': 'None',
                 'product_retailer': 'Update',
                 'product_market_region': 'None',
                 'file': product_csv_file}

    request = factory.post('/tools/import-products/', form_data)
    request.user = create_user()
    view = ProductsView.as_view()
    response = view(request)

    assert response.status_code == 302
    assert Product.objects.count() == 30
    assert update_retailer_prod.retailer.filter(retailer_name='Coop').exists()
    assert create_retailer_prod.retailer.filter(retailer_name='Migros').exists()


@pytest.mark.django_db
def test_product_import_retailer_create():
    update_retailer_prod = mommy.make(Product, gtin=4009233003433)
    retailer = {'retailer_name': 'Walmart'}
    update_retailer_prod.retailer.update(**retailer)

    factory = RequestFactory()

    with open('NutritionService/tests/products_test.csv') as infile:
        product_csv_file = SimpleUploadedFile(infile.name, infile.read())

    form_data = {'product_name_de': 'None',
                 'product_name_en': 'None',
                 'product_name_fr': 'None',
                 'product_name_it': 'None',
                 'product_image': 'None',
                 'product_ingredients': 'None',
                 'product_major': 'None',
                 'product_minor': 'None',
                 'product_weight_unit': 'None',
                 'product_weight_integer': 'None',
                 'product_retailer': 'Create',
                 'product_market_region': 'None',
                 'file': product_csv_file}

    request = factory.post('/tools/import-products/', form_data)
    request.user = create_user()
    view = ProductsView.as_view()
    response = view(request)

    assert response.status_code == 302
    assert Product.objects.count() == 30
    assert not update_retailer_prod.retailer.filter(retailer_name='Coop').exists()


@pytest.mark.django_db
def test_product_import_market_region_update():
    update_market_region_prod = mommy.make(Product, gtin=4009233003433)
    market_region = {'market_region_name': 'Equatorial Guinea'}
    update_market_region_prod.market_region.update(**market_region)

    create_market_region_prod = mommy.make(Product, gtin=9002233011953)

    factory = RequestFactory()

    with open('NutritionService/tests/products_test.csv') as infile:
        product_csv_file = SimpleUploadedFile(infile.name, infile.read())

    form_data = {'product_name_de': 'None',
                 'product_name_en': 'None',
                 'product_name_fr': 'None',
                 'product_name_it': 'None',
                 'product_image': 'None',
                 'product_ingredients': 'None',
                 'product_major': 'None',
                 'product_minor': 'None',
                 'product_weight_unit': 'None',
                 'product_weight_integer': 'None',
                 'product_retailer': 'None',
                 'product_market_region': 'Update',
                 'file': product_csv_file}

    request = factory.post('/tools/import-products/', form_data)
    request.user = create_user()
    view = ProductsView.as_view()
    response = view(request)

    assert response.status_code == 302
    assert Product.objects.count() == 30
    assert update_market_region_prod.market_region.filter(market_region_name='Switzerland').exists()
    assert create_market_region_prod.market_region.filter(market_region_name='Switzerland').exists()


@pytest.mark.django_db
def test_product_import_market_region_create():
    update_market_region_prod = mommy.make(Product, gtin=4009233003433)
    market_region = {'market_region_name': 'Equatorial Guinea'}
    update_market_region_prod.market_region.update(**market_region)

    factory = RequestFactory()

    with open('NutritionService/tests/products_test.csv') as infile:
        product_csv_file = SimpleUploadedFile(infile.name, infile.read())

    form_data = {'product_name_de': 'None',
                 'product_name_en': 'None',
                 'product_name_fr': 'None',
                 'product_name_it': 'None',
                 'product_image': 'None',
                 'product_ingredients': 'None',
                 'product_major': 'None',
                 'product_minor': 'None',
                 'product_weight_unit': 'None',
                 'product_weight_integer': 'None',
                 'product_retailer': 'None',
                 'product_market_region': 'Create',
                 'file': product_csv_file}

    request = factory.post('/tools/import-products/', form_data)
    request.user = create_user()
    view = ProductsView.as_view()
    response = view(request)

    assert response.status_code == 302
    assert Product.objects.count() == 30
    assert not update_market_region_prod.market_region.filter(market_region_name='Switzerland').exists()


@pytest.mark.django_db
def test_product_import_error_logging():
    assert ImportErrorLog.objects.count() == 0
    assert Product.objects.count() == 0

    factory = RequestFactory()

    with open('NutritionService/tests/products_test.csv') as infile:
        product_csv_file = SimpleUploadedFile(infile.name, infile.read())

    form_data = {'product_name_de': 'Update',
                 'product_name_en': 'None',
                 'product_name_fr': 'None',
                 'product_name_it': 'None',
                 'product_image': 'None',
                 'product_ingredients': 'Update',
                 'product_major': 'Update',
                 'product_minor': 'Update',
                 'product_weight_unit': 'Update',
                 'product_weight_integer': 'Update',
                 'product_retailer': 'None',
                 'product_market_region': 'None',
                 'file': product_csv_file}

    request = factory.post('/tools/import-products/', form_data)
    request.user = create_user()
    view = ProductsView.as_view()
    response = view(request)

    assert response.status_code == 302
    assert Product.objects.count() == 30
    assert ImportErrorLog.objects.count() == 36
