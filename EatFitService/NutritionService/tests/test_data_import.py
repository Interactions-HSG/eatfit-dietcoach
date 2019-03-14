from __future__ import print_function
import pytest
import csv
from model_mommy import mommy
from textblob import TextBlob

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory

from NutritionService.data_import import AllergensImport
from NutritionService.forms import AllergensForm, NutrientsForm, ProductsForm
from NutritionService.helpers import store_image_optim, calculate_image_ssim
from NutritionService.models import Product, Allergen, NutritionFact, MajorCategory, MinorCategory, Ingredient, AdditionalImage
from NutritionService.views.utils_view import AllergensView, NutrientsView


def test_allergens_form():

    with open('NutritionService/tests/allergens_test.csv') as infile:
        allergens_csv_file = SimpleUploadedFile(infile.name, infile.read())

    allergens_fields = {'allergen_name': 'on'}
    allergens_file = {'file': allergens_csv_file}
    allergens_form = AllergensForm(allergens_fields, allergens_file)

    assert allergens_form.is_valid()


def test_nutrients_form():

    with open('NutritionService/tests/nutrients_test.csv') as infile:
        nutrients_csv_file = SimpleUploadedFile(infile.name, infile.read())

    nutrients_fields = {'amount': 'on'}
    nutrients_file = {'file': nutrients_csv_file}
    nutrients_form = NutrientsForm(nutrients_fields, nutrients_file)

    assert nutrients_form.is_valid()


def test_products_form():

    with open('NutritionService/tests/products_test.csv') as infile:
        products_csv_file = SimpleUploadedFile(infile.name, infile.read())

    products_fields = {'product_minor': 'on'}
    products_file = {'file': products_csv_file}
    products_form = ProductsForm(products_fields, products_file)

    assert products_form.is_valid()


def test_encoding():

    form_data = {'allergen_name': 'on'}

    bad_file = open('NutritionService/tests/badfile_test.csv')
    bad_test = AllergensImport(bad_file, form_data)

    good_file = open('NutritionService/tests/allergens_test.csv')
    good_test = AllergensImport(good_file, form_data)

    assert not bad_test.check_encoding()
    assert good_test.check_encoding()


def test_headers():

    allergen_data = {'allergen_name': 'on'}

    bad_file = open('NutritionService/tests/nutrients_test.csv')
    bad_test = AllergensImport(bad_file, allergen_data)

    good_file = open('NutritionService/tests/allergens_test.csv')
    good_test = AllergensImport(good_file, allergen_data)

    assert not bad_test.check_headers()
    assert good_test.check_headers()


@pytest.mark.django_db
def test_allergens_import():

    assert Allergen.objects.count() == 0

    mommy.make(Product, id=466560, gtin=5000159431668)

    update_test = mommy.make(Product, id=1019349, gtin=7610807000375)
    mommy.make(Allergen, name='allergenMilk', certainity='false', product=update_test)

    factory = RequestFactory()

    with open('NutritionService/tests/allergens_test.csv') as infile:
        allergens_csv_file = SimpleUploadedFile(infile.name, infile.read())

    form_data = {'allergen_name': 'on',
                 'allergen_certainty': 'on',
                 'file': allergens_csv_file}

    request = factory.post('/tools/import-allergens/', form_data)
    view = AllergensView.as_view()
    response = view(request)

    assert response.status_code == 302
    assert Allergen.objects.count() == 2


@pytest.mark.django_db
def test_nutrient_import():

    assert NutritionFact.objects.count() == 0

    mommy.make(Product, id=494802, gtin=9011900196084)

    update_test = mommy.make(Product, id=1018225, gtin=4335896269665)
    mommy.make(NutritionFact, name='saturated_fat', amount=12.4, unit_of_measure='hl', product=update_test)

    factory = RequestFactory()

    with open('NutritionService/tests/nutrients_test.csv') as infile:
        nutrients_csv_file = SimpleUploadedFile(infile.name, infile.read())

    form_data = {'nutrients_name': 'on',
                 'nutrients_amount': 'on',
                 'nutrients_unit_of_measure': 'on',
                 'file': nutrients_csv_file}

    request = factory.post('/tools/import-nutrients/', form_data)
    view = NutrientsView.as_view()
    response = view(request)

    assert response.status_code == 302
    assert NutritionFact.objects.count() == 2

@pytest.mark.django_db
def test_product():

    Product.objects.create(id=455362, gtin=4008088917148)

    with open('NutritionService/tests/products_test.csv', 'r') as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            if not Product.objects.filter(gtin=int(row['gtin'])).exists():

                # Add location, ingredient

                product_kwargs = {'id': int(row['import_product_id']),
                                  'gtin': int(row['gtin']),
                                  'product_name_de': row['product_name_de'],
                                  'original_image_url': row['imageLink'],
                                  'product_size_unit_of_measure': row['weight_unit'],
                                  'product_size': row['weight_integer']}

                obj_product = Product.objects.create(**product_kwargs)

                if row['imageLink']:
                    store_image_optim(row['imageLink'], obj_product)
                    print(obj_product.image)

                if row['ingredients']:
                    blob = TextBlob(row['ingredients'].decode('utf-8'))
                    lang = blob.detect_language()
                    obj_ingredient = Ingredient.objects.create(product=obj_product, text=row['ingredients'], lang=lang)
                    obj_product.ingredients.add(obj_ingredient)

            else:
                obj_product = Product.objects.filter(gtin=int(row['gtin']))

                update_kwargs = {}

                if obj_product.filter(product_name_de__isnull=True).exists() and row['product_name_de']:
                    update_kwargs.update({'product_name_de': row['product_name_de']})

                if obj_product.filter(original_image_url__isnull=True).exists() and row['imageLink']:
                    update_kwargs.update({'original_image_url': row['imageLink']})

                if obj_product.filter(product_size_unit_of_measure__isnull=True).exists() and row['weight_unit']:
                    update_kwargs.update({'product_size_unit_of_measure': row['weight_unit']})

                if obj_product.filter(product_size__isnull=True).exists() and row['weight_integer']:
                    update_kwargs.update({'product_size': row['weight_integer']})

                # Check ingredient

                if not Ingredient.objects.filter(product=obj_product).exists() and row['ingredients']:
                    blob = TextBlob(row['ingredients'])
                    lang = blob.detect_language()
                    obj_ingredient = Ingredient.objects.create(product=obj_product, text=row['ingredients'], lang=lang)
                    obj_product.ingredients.add(obj_ingredient)

                # Check if image exists

                if obj_product.filter(image__isnull=True).exists() and row['imageLink']:
                    additional_img = store_image_optim(row['imageLink'], obj_product)
                    AdditionalImage(**additional_img).save()
                    if additional_img is not None:
                        additional_img.save()

                obj_product.update(**update_kwargs)

                print(obj_product.values('product_name_de', 'original_image_url',
                                         'product_size_unit_of_measure',
                                         'product_size'))

        assert True
