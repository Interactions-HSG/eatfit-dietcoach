import chardet
import copy
import csv

from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from NutritionService.forms import CSVForm
from NutritionService.models import Product, Allergen


class ImportParser:

    @staticmethod
    def import_allergens(allergen_file, allergen_fields):

        defined_headers = ['import_product_id', 'gtin', 'allergen_name', 'certainity', 'major', 'minor']

        transform_headers = {
            'allergen_name': 'allergen_name',
            'allergen_certainty': 'certainity',
        }

        update_headers = [transform_headers[key] for key, value in allergen_fields.items() if value]

        with open(allergen_file) as csv_import:

            reader = csv.reader(csv_import)

            encoding_detector = chardet.detect(csv_import.read())
            encoding = encoding_detector['encoding']
            header = next(reader, None)

            check_encoding = encoding == 'UTF-8'
            check_headers = set(header) == set(defined_headers)

            if check_headers and check_encoding:
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

            else:
                # log header failure
                # log wrong encoding
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

        allergen_check = any('allergen' in key for key in data.keys())
        nutrients_check = any('nutrients' in key for key in data.keys())
        products_check = any('products' in key for key in data.keys())

        if [allergen_check, nutrients_check, products_check].count(True) > 1:
            # Error: invalid field selection
            return self.form_invalid(form)

        elif [allergen_check, nutrients_check, products_check].count(True) == 0:
            # Error: invalid field selection
            return self.form_invalid(form)

        else:
            if allergen_check:
                allergen_data = {key: value for key, value in data.items() if 'allergen' in key}
                ImportParser.import_allergens(csv_file, allergen_data)

            if nutrients_check:
                nutrient_data = {key: value for key, value in data.items() if 'nutrient' in key}
                ImportParser.import_allergens(csv_file, nutrient_data)

            if products_check:
                product_data = {key: value for key, value in data.items() if 'product' in key}
                ImportParser.import_allergens(csv_file, product_data)

            return super(ImportCSV, self).form_valid(form)  # Python 3: super()
