from __future__ import print_function
import pytest
import csv
from model_mommy import mommy
from textblob import TextBlob

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory

from NutritionService.models import Product, Allergen, NutritionFact, MajorCategory, MinorCategory, Ingredient, AdditionalImage
from NutritionService.helpers import store_image_optim, calculate_image_ssim
from NutritionService.forms import AllergensForm, NutrientsForm, ProductsForm
from NutritionService.views.utils_view import ImportBase, AllergensView, ALLERGEN_HEADERS


def test_forms():

    with open('NutritionService/tests/allergens_test.csv') as infile:
        allergens_csv_file = SimpleUploadedFile(infile.name, infile.read())

    with open('NutritionService/tests/nutrients_test.csv') as infile:
        nutrients_csv_file = SimpleUploadedFile(infile.name, infile.read())

    with open('NutritionService/tests/products_test.csv') as infile:
        products_csv_file = SimpleUploadedFile(infile.name, infile.read())

    allergens_fields = {'allergen_name': True}
    nutrients_fields = {'amount': True}
    products_fields = {'product_minor': True}

    allergens_file = {'file': allergens_csv_file}
    nutrients_file = {'file': nutrients_csv_file}
    products_file = {'file': products_csv_file}

    allergens_form = AllergensForm(allergens_fields, allergens_file)
    nutrients_form = NutrientsForm(nutrients_fields, nutrients_file)
    products_form = ProductsForm(products_fields, products_file)

    assert allergens_form.is_valid()
    assert nutrients_form.is_valid()
    assert products_form.is_valid()


def test_encoding():

    form_data = {'allergen_name': True}

    bad_file = open('NutritionService/tests/badfile_test.csv')
    bad_test = ImportBase(bad_file, form_data)

    good_file = open('NutritionService/tests/allergens_test.csv')
    good_test = ImportBase(good_file, form_data)

    assert not bad_test.check_encoding()
    assert good_test.check_encoding()


def test_headers():

    allergen_data = {'allergen_name': True}

    bad_file = open('NutritionService/tests/badfile_test.csv')
    bad_test = ImportBase(bad_file, allergen_data)
    bad_test.HEADERS = ALLERGEN_HEADERS

    good_file = open('NutritionService/tests/allergens_test.csv')
    good_test = ImportBase(good_file, allergen_data)
    good_test.HEADERS = ALLERGEN_HEADERS

    assert not bad_test.check_headers()
    assert good_test.check_headers()


@pytest.mark.django_db
def test_allergens_import():

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
def test_nutrition():

    with open('NutritionService/tests/nutrients_test.csv', 'r') as infile:
        reader = csv.reader(infile)
        header = next(reader, None)

        for row in reader:
            if Product.objects.filter(gtin=int(row[1])).exists():

                obj_product = Product.objects.get(gtin=int(row[1]))

                if not obj_product.nutrients.filter(name=row[2]).exists():
                    obj_allergen = NutritionFact.objects.create(name=row[2], certainity=row[3], product=obj_product)
                    obj_product.nutrients.add(obj_allergen)

            else:
                obj_product = Product.objects.create(id=int(row[0]), gtin=int(row[1]))
                obj_nutrition = NutritionFact.objects.create(name=row[2], amount=row[3], unit_of_measure=row[4],
                                                             product=obj_product)
                obj_product.nutrients.add(obj_nutrition)

        assert True


@pytest.mark.django_db
def test_product():

    test_case = Product.objects.create(id=455362, gtin=4008088917148)

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

                # if row['major'] != "null" and MajorCategory.objects.filter(pk=row['major']).exists():
                #     obj_major = MajorCategory.objects.get(pk=int(row['major']))
                #     obj_product.major_category.add(obj_major)
                # else:
                #     try:
                #         mommy.make(MajorCategory, pk=int(row['major']))  # Only in test!
                #     except (TypeError, ValueError):
                #         pass
                #
                # if row['minor'] != "null" and MajorCategory.objects.filter(pk=row['minor']).exists():
                #     obj_minor = MinorCategory.objects.get(pk=int(row['minor']))
                #     obj_product.minor_category.add(obj_minor)
                # else:
                #     try:
                #         mommy.make(MinorCategory, pk=int(row['minor']))  # Only in test!
                #     except (TypeError, ValueError):
                #         pass

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

                # Check location



                # # Check major_category
                #
                # if not MajorCategory.objects.filter(product=obj_product).exists() and row['major'] != "null":
                #     obj_major = MajorCategory.objects.get(pk=row['major'])
                #     obj_product.major_category.add(obj_major)
                #
                # # Check minor_category
                #
                # if not MinorCategory.objects.filter(product=obj_product).exists() and row['minor'] != "null":
                #     obj_minor = MajorCategory.objects.get(pk=row['minor'])
                #     obj_product.major_category.add(obj_minor)

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
