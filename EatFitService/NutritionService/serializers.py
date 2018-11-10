from rest_framework import serializers
from NutritionService.models import Product, Allergen, Ingredient, NutritionFact, CrowdsourceProduct, HealthTipp, MajorCategory, MinorCategory, DigitalReceipt

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
    allergens = serializers.SerializerMethodField()
    nutrients = NutritionFactSerializer(many = True, read_only=True)
    weighted_article = serializers.SerializerMethodField('is_weighted_article')
    price = serializers.SerializerMethodField('get_price_value')

    def get_allergens(self, product):
        qs = Allergen.objects.filter(certainity = "true", product = product)
        serializer = AllergenSerializer(instance=qs, many = True)
        return serializer.data
    
    def is_weighted_article(self, obj):
        weighted_article = self.context.get("weighted_article")
        if weighted_article:
            return weighted_article
        return False

    def get_price_value(self, obj):
        price = self.context.get("price")
        if price:
            return price
        return -1

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
            'health_percentage',
            'weighted_article',
            'price'
            ]


class CrowdsourceProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrowdsourceProduct
        fields = '__all__'

class ArticleSerializer(serializers.Serializer):
    article_id = serializers.CharField()
    article_type = serializers.CharField()
    quantity = serializers.FloatField()
    quantity_unit = serializers.CharField()
    price = serializers.FloatField()
    price_currency = serializers.CharField()

class ReceiptSerializer(serializers.Serializer):
    receipt_id = serializers.CharField()
    business_unit = serializers.CharField()
    receipt_datetime = serializers.DateTimeField()
    items = ArticleSerializer(many=True)

class DigitalReceiptSerializer(serializers.Serializer):
    r2n_partner = serializers.CharField()
    r2n_username = serializers.CharField()
    receipts = ReceiptSerializer(many=True)

