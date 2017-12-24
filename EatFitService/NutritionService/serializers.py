
from rest_framework import serializers
from NutritionService.models import Product, Allergen, Ingredient, NutritionFact

class AllergenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergen
        fields = ['name']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['lang', 'text']


class NutritionFactSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionFact
        fields = ["name", "amount", "unit_of_measure"]


class ProductSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)
    allergens = AllergenSerializer(many = True, read_only=True)
    nutrients = NutritionFactSerializer(many = True, read_only=True)

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
            'ingredients',
            'nutrients'
            ]