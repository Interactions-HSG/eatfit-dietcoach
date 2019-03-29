import chardet
import csv

from django.conf import settings
from django.core.mail import send_mail

from NutritionService.helpers import detect_language, store_image_optim
from NutritionService.models import MajorCategory, MinorCategory, Product, ImportErrorLog

ALLERGEN_HEADERS = ['import_product_id', 'gtin', 'allergen_name', 'certainity', 'major', 'minor']
NUTRIENTS_HEADERS = ['import_product_id', 'gtin', 'nutrient_name', 'amount', 'unit_of_measure']
PRODUCT_HEADERS = ['import_product_id', 'gtin', 'product_name_de', 'product_name_en', 'product_name_fr', 'product_name_it', 'weight', 'imageLink', 'ingredients', 'brand', 'description', 'origin', 'category', 'major', 'minor', 'weight_unit', 'weight_integer']

START_SUBJECT = 'Import of {0} has started'  # Change {0} -> {} for python 3
START_MESSAGE = 'This message has been automatically generated'

END_SUBJECT = 'Import of {0} completed'  # Change {0} -> {} for python 3
END_MESSAGE = 'This message has been automatically generated'


# Base interface for imports
class ImportBase:
    HEADERS = None

    def __init__(self, csv_file_path, form_params):
        self.csv_file_path = csv_file_path
        self.form_params = form_params

    def check_encoding(self):

        with open(self.csv_file_path) as csv_file:
            encoding_detector = chardet.detect(csv_file.read())

        encoding = encoding_detector['encoding']
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
        send_mail(subject=START_SUBJECT, message=START_MESSAGE.format(id), from_email=settings.DEFAULT_FROM_EMAIL,
                  recipient_list=['timo.klingler@adnexo.ch'], fail_silently=False, )
        self.import_csv()
        send_mail(subject=END_SUBJECT, message=END_MESSAGE.format(id), from_email=settings.DEFAULT_FROM_EMAIL,
                  recipient_list=['timo.klingler@adnexo.ch'], fail_silently=False, )


class AllergensImport(ImportBase):
    HEADERS = ALLERGEN_HEADERS

    def import_csv(self):

        transform_form_headers = {
            'allergen_name': 'allergen_name',
            'allergen_certainty': 'certainity',
        }
        transform_csv_headers = {
            'allergen_name': 'name',
            'certainity': 'certainity'
        }

        update_headers = [transform_form_headers[key] for key, value in self.form_params.items() if value]

        with open(self.csv_file_path) as csv_file:
            reader = csv.DictReader(csv_file)

            for count, row in enumerate(reader):

                get_row_headers = {header: row[header] for header in update_headers}
                update_allergens = {transform_csv_headers[key]: value for key, value in get_row_headers.items()}

                try:
                    product_object = Product.objects.get(id=int(row['import_product_id']),
                                                         gtin=int(row['gtin']))

                    if product_object.allergens.filter(name=row['allergen_name']).exists():
                        product_object.allergens.update(**update_allergens)
                    else:
                        product_object.allergens.create(**update_allergens)

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


class NutrientsImport(ImportBase):
    HEADERS = NUTRIENTS_HEADERS

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

        update_headers = [transform_form_headers[key] for key, value in self.form_params.items() if value]
        with open(self.csv_file_path) as csv_file:
            reader = csv.DictReader(csv_file)

            for count, row in enumerate(reader):

                get_row_headers = {header: row[header] for header in update_headers}
                update_nutrients = {transform_csv_headers[key]: value for key, value in get_row_headers.items()}

                try:
                    product_object = Product.objects.get(id=int(row['import_product_id']),
                                                         gtin=int(row['gtin']))

                    if product_object.nutrients.filter(name=row['nutrient_name']).exists():
                        product_object.nutrients.update(**update_nutrients)
                    else:
                        product_object.nutrients.create(**update_nutrients)

                except Product.DoesNotExist:

                    log_dict = {
                        'import_type': 'Nutrients',
                        'file_name': csv_file.__str__,
                        'row_data': 'Row ' + str(count) + ': ' + ', '.join(row),
                        'error_field': 'nutrients foreign key field',
                        'error_message': 'Product ' + str(row['gtin']) + ' does not exist.'
                    }
                    ImportErrorLog.objects.create(**log_dict)
                    continue

                except Product.MultipleObjectsReturned:
                    log_dict = {
                        'import_type': 'Nutrients',
                        'file_name': csv_file.__str__,
                        'row_data': 'Row ' + str(count) + ': ' + ', '.join(row),
                        'error_field': 'nutrients foreign key field',
                        'error_message': 'Multiple products with GTIN: ' + str(row['gtin']) + ' found.'
                    }
                    ImportErrorLog.objects.create(**log_dict)
                    continue


class ProductsImport(ImportBase):
    HEADERS = PRODUCT_HEADERS

    def update_or_create_ingredient(self, product, row):

        ingredients_dict = {'text': row['ingredients'],
                            'lang': detect_language(row['ingredients'])}

        if product.ingredients.filter(text=row['ingredients']).exists():
            product.ingredients.update(**ingredients_dict)
        else:
            product.ingredients.create(**ingredients_dict)

    def save_image(self, product, datum):

        store_image_optim(datum, product)

    def update_major_category(self, product, row, csv_file):

        try:
            major_object = MajorCategory.objects.get(id=int(row['major']))

            if product.major_category != major_object:
                product.major_category = major_object

        except MajorCategory.DoesNotExist:

            log_dict = {
                'import_type': 'Products',
                'file_name': csv_file.__str__,
                'row_data': 'Row ' + str(row['counter']) + ': ' + ', '.join(row),
                'error_field': 'major_category',
                'error_message': 'Major category with ID: ' + str(row['major']) + ' does not exist.'
            }
            ImportErrorLog.objects.create(**log_dict)

    def update_minor_category(self, product, row, csv_file):

        try:
            minor_object = MinorCategory.objects.get(id=int(row['minor']))

            if product.minor_category != minor_object:
                product.minor_category = minor_object

        except MinorCategory.DoesNotExist:
            log_dict = {
                'import_type': 'Products',
                'file_name': csv_file.__str__,
                'row_data': 'Row ' + str(row['counter']) + ': ' + ', '.join(row),
                'error_field': 'minor_category',
                'error_message': 'Major category with ID: ' + str(row['minor']) + ' does not exist.'
            }
            ImportErrorLog.objects.create(**log_dict)

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
            'product_weight_integer': 'weight_integer'
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
            'weight_integer': 'product_size'
        }
        safe_update_headers = ['product_name_de', 'product_name_en', 'product_name_fr', 'product_name_it',
                               'product_size_unit_of_measure', 'product_size']

        update_headers = [transform_form_headers[key] for key, value in self.form_params.items() if value]
        with open(self.csv_file_path) as csv_file:
            reader = csv.DictReader(csv_file)

            for count, row in enumerate(reader):

                row.update({'counter': count})
                get_row_headers = {header: row[header] for header in update_headers}
                update_products = {transform_csv_headers[key]: value for key, value in get_row_headers.items()}
                safe_update_products = {key: value for key, value in update_products.items() if
                                        key in safe_update_headers}

                ingredients_update_or_create_condition = row['ingredients'] and 'ingredients' in update_products.keys()
                save_image_condition = row['imageLink'] and 'original_image_url' in update_products.keys()
                major_category_create_condition = row['major'] and row['major'] != 'null'
                minor_category_create_condition = row['minor'] and row['minor'] != 'null'
                major_category_update_condition = major_category_create_condition and 'major' in update_products.keys()
                minor_category_update_condition = minor_category_create_condition and 'minor' in update_products.keys()

                product_object, created = Product.objects.get_or_create(id=int(row['import_product_id']),
                                                                        gtin=int(row['gtin']))

                product_object.__dict__.update(safe_update_products)

                if ingredients_update_or_create_condition:
                    self.update_or_create_ingredient(product_object, row)

                if save_image_condition:
                    self.save_image(product_object, row['imageLink'])

                if (created and major_category_create_condition) or major_category_update_condition:
                    self.update_major_category(product_object, row, csv_file)

                if (created and minor_category_create_condition) or minor_category_update_condition:
                    self.update_minor_category(product_object, row, csv_file)

                product_object.save()
