import chardet
import copy
import csv

from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from NutritionService.forms import CSVForm, ImportTypes
from NutritionService.models import Product, Allergen

ALLERGEN_HEADERS = ['import_product_id', 'gtin', 'allergen_name', 'certainity', 'major', 'minor']
NUTRIENTS_HEADERS = []
PRODUCT_HEADERS = []


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
        check_encoding = encoding == 'UTF-8'
        self.csv_file.seek(0)
        return check_encoding

    def check_headers(self):
        self.csv_file.seek(0)
        reader = csv.reader(self.csv_file)
        header = next(reader, None)
        check_headers = set(header) == set(self.HEADERS)
        self.csv_file.seek(0)
        return check_headers


class AlergenImport(ImportBase):
    HEADERS = ALLERGEN_HEADERS

    def import_csv(self):
        transform_headers = {
            'allergen_name': 'allergen_name',
            'allergen_certainty': 'certainity',
        }

        update_headers = [transform_headers[key] for key, value in self.form_params.items() if value]
        with open(self.csv_file) as csv_import:
            reader = csv.reader(csv_import)
            for row in reader:
                update_allergens = {header: row[header] for header in update_headers}
                try:
                    product_object = Product.objects.get(id=int(row['import_product_id']),
                                                         gtin=int(row['gtin']))

                    if product_object.allergens.filter(name=row['allergen_name']).exists():
                        product_object.allergens.update(**update_allergens)
                    else:
                        allergen_object = Allergen.objects.create(name=row['allergen_name'],
                                                                  certainity=row['certainity'],
                                                                  product=product_object)
                        product_object.allergens.add(allergen_object)

                except product_object.DoesNotExist:
                    # log Product does not exit
                    continue

                except product_object.MultipleObjectsReturned:
                    # log multiple objects
                    continue


class NutrientsImport(ImportBase):
    HEADERS = NUTRIENTS_HEADERS

    def import_csv(csv_file, form_data):
        pass


class ProductsImport(ImportBase):
    HEADERS = PRODUCT_HEADERS

    def import_csv(csv_file, form_data):
        pass


class UtilsList(TemplateView):
    template_name = 'utils/utils_list.html'


class ImportCSV(FormView):
    template_name = 'utils/import_csv.html'
    form_class = CSVForm

    def form_valid(self, form):
        csv_file = form.cleaned_data['file']
        data = copy.copy(form.cleaned_data)
        del data['file']

        import_type = data.get('import_type')

        allergen_check = any('allergen' in key for key in data.keys())
        nutrients_check = any('nutrients' in key for key in data.keys())
        products_check = any('products' in key for key in data.keys())

        # Check whether appropriate fields are filled
        # TODO this can be done with messages
        if [allergen_check, nutrients_check, products_check].count(True) > 1:
            # Error: invalid field selection
            return self.form_invalid(form)

        elif [allergen_check, nutrients_check, products_check].count(True) == 0:
            # Error: invalid field selection
            return self.form_invalid(form)

        else:
            if import_type == ImportTypes.ALLERGEN:
                ImportClass = AlergenImport
                form_data = {key: value for key, value in data.items() if 'allergen' in key}

            elif import_type == ImportTypes.NUTRIENTS:
                ImportClass = NutrientsImport
                form_data = {key: value for key, value in data.items() if 'nutrient' in key}

            elif import_type == ImportTypes.PRODUCTS:
                ImportClass = ProductsImport
                form_data = {key: value for key, value in data.items() if 'product' in key}

            else:
                # TODO handle invalid import type
                pass

            importer = ImportClass(csv_file, form_data)
            importer.check_encoding()
            importer.check_headers()
            importer.import_csv()

            return super(ImportCSV, self).form_valid(form)  # Python 3: super()
