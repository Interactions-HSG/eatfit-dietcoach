from __future__ import print_function
import pytest
import csv
from .models import Product, Allergen, NutritionFact, MajorCategory, MinorCategory, Ingredient
from .helpers import store_image_optim
from model_mommy import mommy
from textblob import TextBlob

@pytest.mark.django_db
def test_allergen():

    with open('final_data_allergen_copy.csv', 'r') as infile:
        reader = csv.reader(infile)
        header = next(reader, None)

        for row in reader:
            if not Product.objects.filter(gtin=int(row[1])).exists():

                obj_product = Product.objects.create(id=int(row[0]), gtin=int(row[1]))
                obj_allergen = Allergen.objects.create(name=row[2], certainity=row[3], product=obj_product)
                obj_product.allergens.add(obj_allergen)

            else:
                obj_product = Product.objects.get(gtin=int(row[1]))

                if not obj_product.allergens.filter(name=row[2]).exists():

                    obj_allergen = Allergen.objects.create(name=row[2], certainity=row[3], product=obj_product)
                    obj_product.allergens.add(obj_allergen)

        assert True


@pytest.mark.django_db
def test_nutrition():

    with open('final_data_nutrition_facts_copy.csv', 'r') as infile:
        reader = csv.reader(infile)
        header = next(reader, None)

        for row in reader:
            if not Product.objects.filter(gtin=int(row[1])).exists():

                obj_product = Product.objects.create(id=int(row[0]), gtin=int(row[1]))
                obj_nutrition = NutritionFact.objects.create(name=row[2], amount=row[3], unit_of_measurement=row[4],
                                                             product=obj_product)
                obj_product.nutrients.add(obj_nutrition)

            else:

                obj_product = Product.objects.get(gtin=int(row[1]))

                if not obj_product.nutrients.filter(name=row[2]).exists():

                    obj_allergen = NutritionFact.objects.create(name=row[2], certainity=row[3], product=obj_product)
                    obj_product.nutrients.add(obj_allergen)

        assert True


@pytest.mark.django_db
def test_product():

    test_case = Product.objects.create(id=455362, gtin=4008088917148)

    with open('final_data_product_copy.csv', 'r') as infile:
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

                if row['ingredient']:
                    blob = TextBlob(row['ingredient'])
                    lang = blob.detect_language()
                    obj_ingredient = Ingredient.objects.create(product=obj_product, text=row['ingredients'], lang=lang)
                    obj_product.ingredients.add(obj_ingredient)

                if row['major'] and MajorCategory.objects.filter(pk=row['major']).exists():
                    obj_major = MajorCategory.objects.get(pk=row['major'])
                    obj_product.major_category.add(obj_major)
                else:
                    mommy.make(MajorCategory, pk=row['major'])  # Only in test!

                if row['minor'] and MajorCategory.objects.filter(pk=row['minor']).exists():
                    obj_minor = MinorCategory.objects.get(pk=row['minor'])
                    obj_product.minor_category.add(obj_minor)
                else:
                    mommy.make(MinorCategory, pk=row['minor'])  # Only in test!

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

                # Check major_category

                if not MajorCategory.objects.filter(product=obj_product).exists() and row['major']:
                    obj_major = MajorCategory.objects.get(pk=row['major'])
                    obj_product.major_category.add(obj_major)

                # Check minor_category

                if not MinorCategory.objects.filter(product=obj_product).exists() and row['minor']:
                    obj_minor = MajorCategory.objects.get(pk=row['minor'])
                    obj_product.major_category.add(obj_minor)

                # Check ingredient

                if not Ingredient.objects.filter(product=obj_product).exists() and row['ingredient']:
                    blob = TextBlob(row['ingredient'])
                    lang = blob.detect_language()
                    obj_ingredient = Ingredient.objects.create(product=obj_product, text=row['ingredients'], lang=lang)
                    obj_product.ingredients.add(obj_ingredient)

                # Check if image exists

                if row['imageLink']:
                    store_image_optim(row['imageLink'], obj_product)

                obj_product.update(**update_kwargs)

                print(obj_product.values('product_name_de', 'original_image_url',
                                         'product_size_unit_of_measure',
                                         'product_size'))
                break

        assert True
