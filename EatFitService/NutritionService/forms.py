from django import forms
from NutritionService.validators import csv_validator

UPDATE_CHOICES = (
    ('Update', 'Update'),
    ('Create', 'Create'),
    ('None', 'None'),
)

UPDATE_CHOICES_LIMITED = (
    ('Update', 'Update'),
    ('None', 'None'),
)


class AllergensForm(forms.Form):
    allergen_name = forms.ChoiceField(choices=UPDATE_CHOICES, label='Allergen Name', widget=forms.RadioSelect)
    allergen_certainty = forms.ChoiceField(choices=UPDATE_CHOICES, label='Allergen Certainty', widget=forms.RadioSelect)
    file = forms.FileField(label="File", validators=[csv_validator])


class NutrientsForm(forms.Form):
    nutrients_name = forms.ChoiceField(choices=UPDATE_CHOICES, label='Nutrient Name', widget=forms.RadioSelect)
    nutrients_amount = forms.ChoiceField(choices=UPDATE_CHOICES, label='Nutrient Amount', widget=forms.RadioSelect)
    nutrients_unit_of_measure = forms.ChoiceField(choices=UPDATE_CHOICES, label='Nutrient Unit of Measure')
    file = forms.FileField(label="File", validators=[csv_validator])


class ProductsForm(forms.Form):
    product_name_de = forms.ChoiceField(choices=UPDATE_CHOICES, label='Product Name (DE)', widget=forms.RadioSelect)
    product_name_en = forms.ChoiceField(choices=UPDATE_CHOICES, label='Product Name (EN)', widget=forms.RadioSelect)
    product_name_fr = forms.ChoiceField(choices=UPDATE_CHOICES, label='Product Name (FR)', widget=forms.RadioSelect)
    product_name_it = forms.ChoiceField(choices=UPDATE_CHOICES, label='Product Name (IT)', widget=forms.RadioSelect)
    product_image = forms.ChoiceField(choices=UPDATE_CHOICES_LIMITED, label='Product Image', widget=forms.RadioSelect)
    product_ingredients = forms.ChoiceField(choices=UPDATE_CHOICES, label='Product Ingredients',
                                            widget=forms.RadioSelect)
    product_major = forms.ChoiceField(choices=UPDATE_CHOICES_LIMITED, label='Product Major Category',
                                      widget=forms.RadioSelect)
    product_minor = forms.ChoiceField(choices=UPDATE_CHOICES_LIMITED, label='Product Minor Category',
                                      widget=forms.RadioSelect)
    product_weight_unit = forms.ChoiceField(choices=UPDATE_CHOICES, label='Product Weight Unit',
                                            widget=forms.RadioSelect)
    product_weight_integer = forms.ChoiceField(choices=UPDATE_CHOICES, label='Product Weight Value',
                                               widget=forms.RadioSelect)
    product_retailer = forms.ChoiceField(choices=UPDATE_CHOICES, label='Product Retailer', widget=forms.RadioSelect)
    product_market_region = forms.ChoiceField(choices=UPDATE_CHOICES, label='Product Market Region',
                                              widget=forms.RadioSelect)
    file = forms.FileField(label="File", validators=[csv_validator])
