from __future__ import print_function
from celery import shared_task
import chardet
import copy
import csv

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from NutritionService.forms import AllergensForm, NutrientsForm, ProductsForm
from NutritionService.models import Product, Allergen

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
                    print('Allergen updated')
                else:
                    product_object.allergens.create(**update_allergens)
                    print('Allergen created')

            except Product.DoesNotExist:
                # log Product does not exit
                print('Product does not exist')
                continue

            except Product.MultipleObjectsReturned:
                print('Multiple objects')
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


class AllergensView(FormView):
    template_name = 'utils/import_allergens.html'
    form_class = AllergensForm
    success_url = reverse_lazy('tools')

    def form_valid(self, form):
        csv_file = form.cleaned_data['file']
        form_data = copy.copy(form.cleaned_data)
        del form_data['file']

        importer = AllergensImport(csv_file, form_data)

        if importer.check_encoding() and importer.check_headers():
            importer.import_csv()
            return super(AllergensView, self).form_valid(form)  # Python 3: super()
        else:
            return self.form_invalid(form)


class NutrientsView(FormView):
    template_name = 'utils/import_nutrients.html'
    form_class = NutrientsForm

    def form_valid(self, form):
        csv_file = form.cleaned_data['file']
        form_data = copy.copy(form.cleaned_data)
        del form_data['file']

        importer = NutrientsImport(csv_file, form_data)

        if importer.check_encoding() and importer.check_headers():
            importer.import_csv()
            return super(NutrientsView, self).form_valid(form)  # Python 3: super()
        else:
            return self.form_invalid(form)


class ProductsView(FormView):
    template_name = 'utils/import_products.html'
    form_class = ProductsForm

    def form_valid(self, form):
        csv_file = form.cleaned_data['file']
        form_data = copy.copy(form.cleaned_data)
        del form_data['file']

        importer = ProductsImport(csv_file, form_data)

        if importer.check_encoding() and importer.check_headers():
            importer.import_csv()
            return super(ProductsView, self).form_valid(form)  # Python 3: super()
        else:
            return self.form_invalid(form)
