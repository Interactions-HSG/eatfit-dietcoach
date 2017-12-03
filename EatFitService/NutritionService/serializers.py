
from rest_framework import serializers
from NutritionService.models import Product, Allergen, Ingridient, NutritionFact

class AllergenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergen
        fields = ['name']


class IngridientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingridient
        fields = ['lang', 'text']


class NutritionFactSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionFact
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    ingridients = IngridientSerializer(many=True, read_only=True)
    allergens = AllergenSerializer(many = True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'gtin',
            'product_name_en',
            'product_name_de',
            'product_name_fr',
            'product_name_it',
            'producer',
            'product_size',
            'product_size_unit_of_measure',
            'serving_size',
            'comment',
            'image',
            'major_category',
            'minor_category',
            'allergens',
            'ingridients'
            ]