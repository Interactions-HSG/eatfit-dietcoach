from __future__ import print_function
import pytest
import csv
from model_mommy import mommy
from textblob import TextBlob
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile

from NutritionService.models import Product, Allergen, NutritionFact, MajorCategory, MinorCategory, Ingredient, AdditionalImage
from NutritionService.helpers import store_image_optim, calculate_image_ssim
from NutritionService.forms import CSVForm
from NutritionService.views.utils_view import ImportBase, ALLERGEN_HEADERS


def test_encoding():

    form_data = {'import_type': 'Allergens',
                 'allergen_name': True}

    bad_file = open('NutritionService/tests/badfile_test.csv')
    bad_test = ImportBase(bad_file, form_data)

    good_file = open('NutritionService/tests/allergens_test.csv')
    good_test = ImportBase(good_file, form_data)

    assert not bad_test.check_encoding()
    assert good_test.check_encoding()


def test_headers():

    allergen_data = {'import_type': 'Allergens',
                     'allergen_name': True}

    bad_file = open('NutritionService/tests/badfile_test.csv')
    bad_test = ImportBase(bad_file, allergen_data)
    bad_test.HEADERS = ALLERGEN_HEADERS

    good_file = open('NutritionService/tests/allergens_test.csv')
    good_test = ImportBase(good_file, allergen_data)
    good_test.HEADERS = ALLERGEN_HEADERS

    assert not bad_test.check_headers()
    assert good_test.check_headers()


def test_form():

    # Test allergens

    with open('NutritionService/tests/allergens_test.csv') as infile:
        allergen_csv_file = SimpleUploadedFile(infile.name, infile.read())

    allergen_fields = {'import_type': 'Allergens',
                       'allergen_name': True}

    allergen_file = {'file': allergen_csv_file}

    allergen_form = CSVForm(allergen_fields, allergen_file)

    assert allergen_form.is_valid()

# @pytest.mark.django_db
# def test_allergen():
#
#     with open('NutritionService/tests/allergens_test.csv', 'r') as infile:
#         reader = csv.reader(infile)
#         header = next(reader, None)
#
#         for row in reader:
#             if Product.objects.filter(gtin=int(row[1])).exists():
#
#                 obj_product = Product.objects.get(gtin=int(row[1]))
#
#                 if not obj_product.allergens.filter(name=row[2]).exists():
#                     obj_allergen = Allergen.objects.create(name=row[2], certainity=row[3], product=obj_product)
#                     obj_product.allergens.add(obj_allergen)
#             else:
#                 obj_product = Product.objects.create(id=int(row[0]), gtin=int(row[1]))
#                 obj_allergen = Allergen.objects.create(name=row[2], certainity=row[3], product=obj_product)
#                 obj_product.allergens.add(obj_allergen)
#
#         assert True


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
