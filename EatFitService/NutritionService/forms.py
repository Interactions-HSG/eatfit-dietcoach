from django import forms
from NutritionService.validators import csv_validator


class AllergensForm(forms.Form):
    allergen_name = forms.BooleanField(label='Allergen Name', required=False)
    allergen_certainty = forms.BooleanField(label='Allergen Certainty', required=False)
    file = forms.FileField(label="File", validators=[csv_validator])


class NutrientsForm(forms.Form):
    nutrients_name = forms.BooleanField(label='Nutrient Name', required=False)
    nutrients_amount = forms.BooleanField(label='Nutrient Amount', required=False)
    nutrients_unit_of_measure = forms.BooleanField(label='Nutrient Unit of Measure', required=False)
    file = forms.FileField(label="File", validators=[csv_validator])


class ProductsForm(forms.Form):
    product_name_de = forms.BooleanField(label='Product Name (DE)', required=False)
    product_name_en = forms.BooleanField(label='Product Name (EN)', required=False)
    product_name_fr = forms.BooleanField(label='Product Name (FR)', required=False)
    product_name_it = forms.BooleanField(label='Product Name (IT)', required=False)
    product_image = forms.BooleanField(label='Product Image', required=False)
    product_ingredients = forms.BooleanField(label='Product Ingredients', required=False)
    product_major = forms.BooleanField(label='Product Major Category', required=False)
    product_minor = forms.BooleanField(label='Product Minor Category', required=False)
    product_weight_unit = forms.BooleanField(label='Product Weight Unit', required=False)
    product_weight_integer = forms.BooleanField(label='Product Weight Value', required=False)
    file = forms.FileField(label="File", validators=[csv_validator])
