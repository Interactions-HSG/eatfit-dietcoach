from __future__ import print_function
import copy
import os

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from NutritionService.data_import import AllergensImport, NutrientsImport, ProductsImport
from NutritionService.forms import AllergensForm, NutrientsForm, ProductsForm
from NutritionService.tasks import execute_allergen_import_task, execute_nutrient_import_task, execute_product_import_task


class UtilsList(LoginRequiredMixin, TemplateView):
    template_name = 'utils/utils_list.html'


def save_uploaded_file(file):

    location = os.path.join(settings.BASE_DIR, 'imports')
    fs = FileSystemStorage(location=location, base_url=location)

    filename = fs.save(file.name, file)
    file_path = fs.url(filename)

    return file_path


class AllergensView(LoginRequiredMixin, FormView):
    template_name = 'utils/import_allergens.html'
    form_class = AllergensForm
    success_url = reverse_lazy('tools')

    def form_valid(self, form):

        csv_file = self.request.FILES['file']
        form_data = copy.copy(form.cleaned_data)
        del form_data['file']

        # Persist file to disk
        file_path = save_uploaded_file(csv_file)

        importer = AllergensImport(file_path, form_data)

        if importer.check_encoding() and importer.check_headers():
            execute_allergen_import_task.delay(file_path, form_data)
            return super(AllergensView, self).form_valid(form)  # Python 3: super()
        else:
            return self.form_invalid(form)


class NutrientsView(LoginRequiredMixin, FormView):
    template_name = 'utils/import_nutrients.html'
    form_class = NutrientsForm
    success_url = reverse_lazy('tools')

    def form_valid(self, form):
        csv_file = self.request.FILES['file']
        form_data = copy.copy(form.cleaned_data)
        del form_data['file']

        # Persist file to disk
        file_path = save_uploaded_file(csv_file)

        importer = NutrientsImport(file_path, form_data)

        if importer.check_encoding() and importer.check_headers():
            execute_nutrient_import_task.delay(file_path, form_data)
            return super(NutrientsView, self).form_valid(form)  # Python 3: super()
        else:
            return self.form_invalid(form)


class ProductsView(LoginRequiredMixin, FormView):
    template_name = 'utils/import_products.html'
    form_class = ProductsForm
    success_url = reverse_lazy('tools')

    def form_valid(self, form):
        csv_file = self.request.FILES['file']
        form_data = copy.copy(form.cleaned_data)
        del form_data['file']

        # Persist file to disk

        file_path = save_uploaded_file(csv_file)

        importer = ProductsImport(file_path, form_data)

        if importer.check_encoding() and importer.check_headers():
            execute_product_import_task.delay(file_path, form_data)
            return super(ProductsView, self).form_valid(form)  # Python 3: super()
        else:
            return self.form_invalid(form)
