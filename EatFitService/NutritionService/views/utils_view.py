from __future__ import print_function
import copy
import tempfile

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from NutritionService.data_import import AllergensImport, NutrientsImport, ProductsImport, execute_allergen_import_task
from NutritionService.forms import AllergensForm, NutrientsForm, ProductsForm


class UtilsList(LoginRequiredMixin, TemplateView):
    template_name = 'utils/utils_list.html'


class AllergensView(LoginRequiredMixin, FormView):
    template_name = 'utils/import_allergens.html'
    form_class = AllergensForm
    success_url = reverse_lazy('tools')

    def form_valid(self, form):

        with tempfile.NamedTemporaryFile(delete=False) as csv_file:
            for chunk in form.cleaned_data['file']:
                csv_file.write(chunk)

        form_data = copy.copy(form.cleaned_data)
        del form_data['file']

        importer = AllergensImport(csv_file.name, form_data)

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
        csv_file = form.cleaned_data['file']
        form_data = copy.copy(form.cleaned_data)
        del form_data['file']

        importer = NutrientsImport(csv_file, form_data)

        if importer.check_encoding() and importer.check_headers():
            execute_import_task.delay(importer)
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

        importer = ProductsImport(csv_file, form_data)

        if importer.check_encoding() and importer.check_headers():
            execute_import_task.delay(importer)
            return super(ProductsView, self).form_valid(form)  # Python 3: super()
        else:
            return self.form_invalid(form)
