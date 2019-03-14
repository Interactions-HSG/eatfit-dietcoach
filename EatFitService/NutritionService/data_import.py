import chardet
import csv

from NutritionService.helpers import detect_language, store_image, store_additional_image, store_image_optim
from NutritionService.models import Product, MajorCategory, MinorCategory

ALLERGEN_HEADERS = ['import_product_id', 'gtin', 'allergen_name', 'certainity', 'major', 'minor']
NUTRIENTS_HEADERS = ['import_product_id', 'gtin', 'nutrient_name', 'amount', 'unit_of_measure']
PRODUCT_HEADERS = ['import_product_id', 'gtin', 'product_name_de', 'weight', 'imageLink', 'ingredients', 'brand',
                   'description', 'origin', 'category', 'major', 'minor', 'weight_unit', 'weight_integer']


# Base interface for imports
class ImportBase:
    HEADERS = None

    def __init__(self, csv_file, form_params):
        self.csv_file = csv_file
        self.form_params = form_params

    def check_encoding(self):
        self.csv_file.seek(0)
        encoding_detector = chardet.detect(self.csv_file.read())
        encoding = encoding_detector['encoding']
        check_encoding = True if encoding.find('UTF-8') == 0 or encoding.find('ascii') == 0 else False
        self.csv_file.seek(0)
        return check_encoding

    def check_headers(self):
        self.csv_file.seek(0)
        reader = csv.reader(self.csv_file)
        header = next(reader, None)
        check_headers = set(header) == set(self.HEADERS)
        self.csv_file.seek(0)
        return check_headers


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
        reader = csv.DictReader(self.csv_file)

        for row in reader:

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
                # log Product does not exit
                continue

            except Product.MultipleObjectsReturned:
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
        reader = csv.DictReader(self.csv_file)

        for row in reader:

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
                # log Product does not exit
                continue

            except Product.MultipleObjectsReturned:
                continue


class ProductsImport(ImportBase):
    HEADERS = PRODUCT_HEADERS

    def import_csv(self):
        transform_form_headers = {
            'product_name_de': 'product_name_de',
            'product_image': 'imageLink',
            'product_ingredients': 'ingredients',
            'product_major': 'major',
            'product_minor': 'minor',
            'product_weight_unit': 'weight_unit',
            'product_weight_integer': 'weight_integer'
        }
        transform_csv_headers = {
            'product_name_de': 'product_name_de',
            'imageLink': 'original_image_url',
            'ingredients': 'ingredients',
            'major': 'major',
            'minor': 'minor',
            'weight_unit': 'product_size_unit_of_measure',
            'weight_integer': 'product_size'
        }
        safe_update_headers = ['product_name_de', 'product_size_unit_of_measure', 'product_size']

        update_headers = [transform_form_headers[key] for key, value in self.form_params.items() if value]
        reader = csv.DictReader(self.csv_file)

        for row in reader:

            get_row_headers = {header: row[header] for header in update_headers}
            update_products = {transform_csv_headers[key]: value for key, value in get_row_headers.items()}
            safe_update_products = {update_products[key]: value for key, value in update_products.items() if key in safe_update_headers}

            ingredient_condition = row['ingredients'] and 'ingredients' in update_products.keys()
            image_condition = row['imageLink'] and 'original_image_url' in update_products.keys()
            major_category_condition = row['major'] and 'major' in update_products.keys()
            minor_category_condition = row['minor'] and 'minor' in update_products.keys()

            try:
                product_object = Product.objects.get(id=int(row['import_product_id']),
                                                     gtin=int(row['gtin']))

                product_object.update(**safe_update_products)

                if ingredient_condition:
                    ingredients_dict = {'text': row['ingredients'],
                                        'lang': detect_language(row['ingredients'])}

                    if product_object.ingredients.filter(text=row['ingredients']).exists():
                        product_object.ingredients.update(**ingredients_dict)
                    else:
                        product_object.ingredients.create(**ingredients_dict)

                if image_condition:
                    main_image_condition = product_object.filter(original_image_url=row['imageLink']).exists()
                    additional_image_condition = product_object.additional_image.filter(image_url=row['imageLink']).exists()

                    if main_image_condition:

                        if product_object.image:
                            # Calculate structural similarity
                            store_image_optim(row['imageLink'], product_object)
                        else:
                            store_image(row['imageLink'], product_object)

                    if not additional_image_condition:
                        store_additional_image(row['imageLink'], product_object)

                if major_category_condition:

                    try:
                        major_object = MajorCategory.object.get(id=int(row['major']))

                        if not product_object.major_category.filter(id=int(row['major'])).exists():
                            product_object.major_category.update(major_object)

                    except MajorCategory.DoesNotExist:
                        # Log wrong major category
                        pass

                if minor_category_condition:

                    try:
                        minor_object = MinorCategory.object.get(id=int(row['minor']))

                        if not product_object.minor_category.filter(id=int(row['minor'])).exists():
                            product_object.minor_category.update(minor_object)

                    except MinorCategory.DoesNotExist:
                        # Log wrong minor category
                        pass

            except Product.DoesNotExist:
                product_object = Product.objects.create(id=int(row['import_product_id']),
                                                        gtin=int(row['gtin']))

                product_object.update(**safe_update_products)

                if ingredient_condition:
                    ingredients_dict = {'text': row['ingredients'],
                                        'lang': detect_language(row['ingredients'])}
                    product_object.ingredients.create(**ingredients_dict)

                if image_condition:
                    store_image_optim(row['imageLink'], product_object)

                if major_category_condition:

                    try:
                        major_object = MajorCategory.object.get(id=int(row['major']))
                        product_object.major_category.update(major_object)

                    except MajorCategory.DoesNotExist:
                        # Log wrong major category
                        pass

                if minor_category_condition:

                    try:
                        minor_object = MajorCategory.object.get(id=int(row['minor']))
                        product_object.major_category.update(minor_object)

                    except MinorCategory.DoesNotExist:
                        # Log wrong minor category
                        pass

            except Product.MultipleObjectsReturned:
                # Log multiple product object existence
                continue
