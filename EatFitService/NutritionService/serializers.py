
from rest_framework import serializers
from NutritionService.models import Product, Allergen, Ingredient, NutritionFact, CrowdsourceProduct, HealthTipp, MajorCategory, MinorCategory

class AllergenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergen
        fields = ['name']

class MajorCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MajorCategory
        fields = '__all__'

class MinorCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MinorCategory
        fields = '__all__'

class HealthTippSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthTipp
        fields = ['text_de', 'text_en', 'text_fr', 'text_it', 'image']


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
            'back_image',
            'major_category',
            'minor_category',
            'allergens',
            'ingredients',
            'nutrients',
            'ofcom_value',
            'source',
            'source_checked',
            'health_percentage'
            ]


class CrowdsourceProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrowdsourceProduct
        fields = '__all__'
