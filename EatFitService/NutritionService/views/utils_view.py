from __future__ import print_function
import copy
import tempfile
import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from NutritionService.data_import import AllergensImport, NutrientsImport, ProductsImport
from NutritionService.forms import AllergensForm, NutrientsForm, ProductsForm
from NutritionService.tasks import execute_allergen_import_task


class UtilsList(LoginRequiredMixin, TemplateView):
    template_name = 'utils/utils_list.html'


def save_uploaded_file(file):
    # Persist file to disk
    file_path = tempfile.mktemp()
    fd = open(file_path, "w")
    fd.write(file.read())
    fd.flush()
    fd.close()
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
            execute_allergen_import_task.delay(csv_file.name, form_data)
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
            importer.execute_import()
            return super(NutrientsView, self).form_valid(form)  # Python 3: super()
        else:
            return self.form_invalid(form)


class ProductsView(LoginRequiredMixin, FormView):
    template_name = 'utils/import_products.html'
    form_class = ProductsForm
    success_url = reverse_lazy('tools')

    def form_valid(self, form):
        csv_file = form.cleaned_data['file']
        form_data = copy.copy(form.cleaned_data)
        del form_data['file']

        # Persist file to disk
        file_path = save_uploaded_file(csv_file)

        importer = ProductsImport(file_path, form_data)

        if importer.check_encoding() and importer.check_headers():
            importer.execute_import()
            return super(ProductsView, self).form_valid(form)  # Python 3: super()
        else:
            return self.form_invalid(form)
