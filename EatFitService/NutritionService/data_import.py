import chardet
import csv

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q

from NutritionService.helpers import detect_language, store_image_optim, store_image
from NutritionService.models import MajorCategory, MinorCategory, Product, ImportErrorLog

ALLERGEN_HEADERS = ['import_product_id', 'gtin', 'allergen_name', 'certainity', 'major', 'minor']
NUTRIENTS_HEADERS = ['import_product_id', 'gtin', 'nutrient_name', 'amount', 'unit_of_measure']
PRODUCT_HEADERS = ['import_product_id', 'gtin', 'product_name_de', 'product_name_en', 'product_name_fr',
                   'product_name_it', 'weight', 'imageLink', 'ingredients', 'brand', 'description', 'origin',
                   'category', 'major', 'minor', 'weight_unit', 'weight_integer', 'retailer', 'market_region']

START_SUBJECT = 'Import has started: '  # Change {0} -> {} for python 3
START_MESSAGE = 'This message has been automatically generated'

END_SUBJECT = 'Import complete: '  # Change {0} -> {} for python 3
END_MESSAGE = 'This message has been automatically generated'


# Base interface for imports
class ImportBase:
    HEADERS = None

    def __init__(self, csv_file_path, form_params):
        self.csv_file_path = csv_file_path
        self.form_params = form_params

    def check_encoding(self):
        with open(self.csv_file_path) as csv_file:
            detector = chardet.universaldetector.UniversalDetector()
            # check only first 30 lines for encoding
            for line in csv_file.readlines()[:30]:
                detector.feed(line)
        detector.close()
        encoding = detector.result['encoding']
        check_encoding = True if encoding.find('utf-8') == 0 or encoding.find('ascii') == 0 else False

        return check_encoding

    def check_headers(self):
        with open(self.csv_file_path) as csv_file:
            reader = csv.DictReader(csv_file)
            header = reader.fieldnames

        check_headers = set(header) == set(self.HEADERS)

        return check_headers

    def import_csv(self):
        pass

    def execute_import(self, id='UNKNOWN'):
        send_mail(subject=START_SUBJECT, message=START_MESSAGE + id, from_email=settings.DEFAULT_FROM_EMAIL,
                  recipient_list=['klaus.fuchs@autoidlabs.ch'], fail_silently=False, )
        self.import_csv()
        send_mail(subject=END_SUBJECT, message=END_MESSAGE + id, from_email=settings.DEFAULT_FROM_EMAIL,
                  recipient_list=['klaus.fuchs@autoidlabs.ch'], fail_silently=False, )


class AllergensImport(ImportBase):
    HEADERS = ALLERGEN_HEADERS

    def update_or_create_fields(self, product, update_dict):

        product.allergens.update_or_create(**update_dict)

    def create_fields(self, product, create_dict):

        try:
            allergens = list(product.allergens.filter(name=create_dict['name']))

            for allergen in allergens:
                if allergens.certainity is None:
                    allergen.certainity = create_dict['certainity']
                    allergen.save()

        except KeyError:
            pass

    def import_csv(self):

        transform_form_headers = {
            'allergen_name': 'allergen_name',
            'allergen_certainty': 'certainity',
        }
        transform_csv_headers = {
            'allergen_name': 'name',
            'certainity': 'certainity'
        }

        update_headers = [transform_form_headers[key] for key, value in self.form_params.items() if value == 'Update']
        create_headers = [transform_form_headers[key] for key, value in self.form_params.items() if value == 'Create']

        with open(self.csv_file_path) as csv_file:
            reader = csv.DictReader(csv_file)

            for count, row in enumerate(reader):
                try:
                    update_row_headers = {header: row[header] for header in update_headers}
                    update_allergens = {transform_csv_headers[key]: value for key, value in update_row_headers.items()}

                    create_row_headers = {header: row[header] for header in create_headers}
                    create_allergens = {transform_csv_headers[key]: value for key, value in create_row_headers.items()}

                    try:
                        product_object = Product.objects.get(gtin=int(row['gtin']))

                        if update_allergens:
                            self.update_or_create_fields(product_object, update_allergens)

                        if create_allergens:
                            self.create_fields(product_object, create_allergens)

                    except Product.DoesNotExist:

                        log_dict = {
                            'import_type': 'Allergens',
                            'file_name': self.csv_file_path,
                            'row_data': 'Row ' + str(count) + ': ' + ', '.join(row),
                            'error_field': 'allergens foreign key field',
                            'error_message': 'Product ' + str(row['gtin']) + ' does not exist.'
                        }
                        ImportErrorLog.objects.create(**log_dict)
                        continue

                    except Product.MultipleObjectsReturned:

                        log_dict = {
                            'file_name': self.csv_file_path,
                            'import_type': 'Allergens',
                            'row_data': 'Row ' + str(count) + ': ' + ', '.join(row),
                            'error_field': 'allergens foreign key field',
                            'error_message': 'Multiple products with ' + str(row['gtin']) + ' found.'
                        }
                        ImportErrorLog.objects.create(**log_dict)
                        continue
                except:
                    continue

class NutrientsImport(ImportBase):
    HEADERS = NUTRIENTS_HEADERS

    def update_or_create_fields(self, product, update_dict):

        product.nutrients.update_or_create(**update_dict)

    def create_fields(self, product, create_dict):

        try:
            nutrients = list(product.nutrients.filter(name=create_dict['name']))

            for nutrient in nutrients:
                if nutrient.amount is None:
                    nutrient.amount = create_dict['amount']
                    nutrient.save()
                if nutrient.unit_of_measure is None:
                    nutrient.amount = create_dict['unit_of_measure']
                    nutrient.save()

        except KeyError:
            pass

    def import_csv(self):
        transform_form_headers = {
            'nutrients_name': 'nutrient_name',
            'nutrients_amount': 'amount',
            'nutrients_unit_of_measure': 'unit_of_measure'
        }
        transform_csv_headers = {
            'nutrient_name': 'name',
            'amount': 'amount',
            'unit_of_measure': 'unit_of_measure'
        }

        update_headers = [transform_form_headers[key] for key, value in self.form_params.items() if value == 'Update']
        create_headers = [transform_form_headers[key] for key, value in self.form_params.items() if value == 'Create']

        with open(self.csv_file_path) as csv_file:
            reader = csv.DictReader(csv_file)

            for count, row in enumerate(reader):
                try:
                    update_row_headers = {header: row[header] for header in update_headers}
                    update_nutrients = {transform_csv_headers[key]: value for key, value in update_row_headers.items()}

                    create_row_headers = {header: row[header] for header in create_headers}
                    create_nutrients = {transform_csv_headers[key]: value for key, value in create_row_headers.items()}

                    try:
                        product_object = Product.objects.get(gtin=int(row['gtin']))

                        if update_nutrients:
                            self.update_or_create_fields(product_object, update_nutrients)

                        if create_nutrients:
                            self.create_fields(product_object, create_nutrients)

                    except Product.DoesNotExist:

                        log_dict = {
                            'import_type': 'Nutrients',
                            'file_name': self.csv_file_path,
                            'row_data': 'Row ' + str(count) + ': ' + ', '.join(row),
                            'error_field': 'nutrients foreign key field',
                            'error_message': 'Product ' + str(row['gtin']) + ' does not exist.'
                        }
                        ImportErrorLog.objects.create(**log_dict)
                        continue

                    except Product.MultipleObjectsReturned:
                        log_dict = {
                            'import_type': 'Nutrients',
                            'file_name': self.csv_file_path,
                            'row_data': 'Row ' + str(count) + ': ' + ', '.join(row),
                            'error_field': 'nutrients foreign key field',
                            'error_message': 'Multiple products with GTIN: ' + str(row['gtin']) + ' found.'
                        }
                        ImportErrorLog.objects.create(**log_dict)
                        continue
                except:
                    continue

class ProductsImport(ImportBase):
    HEADERS = PRODUCT_HEADERS

    def update_or_create_ingredient(self, product, row):

        ingredients_dict = {'text': row['ingredients'],
                            'lang': detect_language(row['ingredients'])}

        product.ingredients.update_or_create(**ingredients_dict)

    def create_ingredient(self, product, row):

        ingredients_dict = {'text': row['ingredients'],
                            'lang': detect_language(row['ingredients'])}

        if product.ingredients.filter(text__isnull=True, lang__isnull=True).exists():
            product.ingredients.create(**ingredients_dict)

    def update_or_create_image(self, product, datum):

        store_image_optim(datum, product)

    def update_major_category(self, product, row):

        try:
            major_object = MajorCategory.objects.get(id=int(row['major']))

            if product.major_category != major_object:
                product.major_category = major_object

        except MajorCategory.DoesNotExist:

            log_dict = {
                'import_type': 'Products',
                'file_name': self.csv_file_path,
                'row_data': 'Row ' + str(row['counter']) + ': ' + ', '.join(row),
                'error_field': 'major_category',
                'error_message': 'Major category with ID: ' + str(row['major']) + ' does not exist.'
            }
            ImportErrorLog.objects.create(**log_dict)

    def update_minor_category(self, product, row):

        try:
            minor_object = MinorCategory.objects.get(id=int(row['minor']))

            if product.minor_category != minor_object:
                product.minor_category = minor_object

        except MinorCategory.DoesNotExist:
            log_dict = {
                'import_type': 'Products',
                'file_name': self.csv_file_path,
                'row_data': 'Row ' + str(row['counter']) + ': ' + ', '.join(row),
                'error_field': 'minor_category',
                'error_message': 'Major category with ID: ' + str(row['minor']) + ' does not exist.'
            }
            ImportErrorLog.objects.create(**log_dict)

    def update_or_create_retailer(self, product, row):

            product.retailer.update_or_create(retailer_name=row['retailer'])

    def create_retailer(self, product, row):

        if product.retailer.filter(retailer_name__isnull=True).exists():
            product.retailer.create(retailer_name=row['retailer'])

    def update_or_create_market_region(self, product, row):

        market_regions = ['Switzerland', 'Germany', 'Austria', 'France', 'Italy']
        market_region_name = row['market_region'] if row['market_region'] in market_regions else 'Switzerland'

        product.market_region.update_or_create(market_region_name=market_region_name)

    def create_market_region(self, product, row):

        market_regions = ['Switzerland', 'Germany', 'Austria', 'France', 'Italy']
        market_region_name = row['market_region'] if row['market_region'] in market_regions else 'Switzerland'

        if product.market_region.filter(market_region_name__isnull=True).exists():
            product.market_region.create(market_region_name=market_region_name)

    def import_csv(self):
        transform_form_headers = {
            'product_name_de': 'product_name_de',
            'product_name_en': 'product_name_en',
            'product_name_fr': 'product_name_fr',
            'product_name_it': 'product_name_it',
            'product_image': 'imageLink',
            'product_ingredients': 'ingredients',
            'product_major': 'major',
            'product_minor': 'minor',
            'product_weight_unit': 'weight_unit',
            'product_weight_integer': 'weight_integer',
            'product_retailer': 'retailer',
            'product_market_region': 'market_region'
        }
        transform_csv_headers = {
            'product_name_de': 'product_name_de',
            'product_name_en': 'product_name_en',
            'product_name_fr': 'product_name_fr',
            'product_name_it': 'product_name_it',
            'imageLink': 'original_image_url',
            'ingredients': 'ingredients',
            'major': 'major',
            'minor': 'minor',
            'weight_unit': 'product_size_unit_of_measure',
            'weight_integer': 'product_size',
            'retailer': 'retailer',
            'market_region': 'market_region'
        }
        safe_headers = ['product_name_de', 'product_name_en', 'product_name_fr', 'product_name_it',
                        'product_size_unit_of_measure', 'product_size']

        update_headers = [transform_form_headers[key] for key, value in self.form_params.items() if value == 'Update']
        create_headers = [transform_form_headers[key] for key, value in self.form_params.items() if value == 'Create']

        with open(self.csv_file_path) as csv_file:
            reader = csv.DictReader(csv_file)

            for count, row in enumerate(reader):
                try:
                    row.update({'counter': count})

                    update_row_headers = {header: row[header] for header in update_headers}
                    update_products = {transform_csv_headers[key]: value for key, value in update_row_headers.items()}

                    create_row_headers = {header: row[header] for header in create_headers}
                    create_products = {transform_csv_headers[key]: value for key, value in create_row_headers.items()}

                    safe_update_products = {key: value for key, value in update_products.items() if key in safe_headers}
                    safe_create_products = {key: value for key, value in create_products.items() if key in safe_headers}

                    ingredients_update_condition = row['ingredients'] is not None and 'ingredients' in update_products.keys()
                    image_update_condition = row['imageLink'] is not None and 'original_image_url' in update_products.keys()
                    major_category_base_condition = row['major'] is not None and row['major'] != 'null'
                    minor_category_base_condition = row['minor'] is not None and row['minor'] != 'null'
                    major_category_update_condition = major_category_base_condition and 'major' in update_products.keys()
                    minor_category_update_condition = minor_category_base_condition and 'minor' in update_products.keys()
                    retailer_update_condition = row['retailer'] is not None and 'retailer' in update_products.keys()
                    market_region_update_condition = row['market_region'] is not None and 'market_region' in update_products.keys()

                    ingredients_create_condition = row['ingredients'] is not None and 'ingredients' in create_products.keys()
                    retailer_create_condition = row['retailer'] is not None and 'retailer' in create_products.keys()
                    market_region_create_condition = row['market_region'] is not None and 'market_region' in create_products.keys()

                    product_object, created = Product.objects.get_or_create(gtin=int(row['gtin']))

                    # Safe update
                    product_object.__dict__.update(safe_update_products)

                    # Safe create
                    for key, value in safe_create_products.items():
                        if product_object.__dict__.get(key) is None:
                            product_object.__dict__.update({key: value})

                    if ingredients_update_condition:
                        self.update_or_create_ingredient(product_object, row)

                    if ingredients_create_condition:
                        self.create_ingredient(product_object, row)

                    if image_update_condition:
                        self.update_or_create_image(product_object, row['imageLink'])

                    if (created and major_category_base_condition) or major_category_update_condition:
                        self.update_major_category(product_object, row)

                    if (created and minor_category_base_condition) or minor_category_update_condition:
                        self.update_minor_category(product_object, row)

                    if retailer_update_condition:
                        self.update_or_create_retailer(product_object, row)

                    if retailer_create_condition:
                        self.create_retailer(product_object, row)

                    if market_region_update_condition:
                        self.update_or_create_market_region(product_object, row)

                    if market_region_create_condition:
                        self.create_market_region(product_object, row)

                    product_object.save()
                except:
                    continue