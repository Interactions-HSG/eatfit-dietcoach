from rest_framework import serializers
from TrustBoxAPI.models import NutritionAttribute
from TrustBoxAPI.models import NutritionFact
from TrustBoxAPI.models import NutritionGroupAttribute
from TrustBoxAPI.models import NutritionFactsGroup
from TrustBoxAPI.models import Nutrition
from TrustBoxAPI.models import ProductAttribute
from TrustBoxAPI.models import Product, ImportLog, ProductName
from SaltTrackerService.models import ShoppingTip

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductName
        fields = '__all__'

class ProductWithNameSerializer(serializers.ModelSerializer):
    gtin = serializers.IntegerField(source="product.gtin")

    class Meta:
        model = ProductName
        fields = '__all__'

class ImportLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportLog
        fields = '__all__'

class ShoppingTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingTip
        fields = ("text", "nwd_subcategory_name", "category_color", "icon")


class ProductNameImportSerializer(serializers.ModelSerializer):
    _languageCode = serializers.CharField(source="language_code")

    class Meta:
        model = ProductName
        fields = ("_languageCode", "name")

class ProductAttributeImportSerializer(serializers.ModelSerializer):
    _canonicalName = serializers.CharField(source="canonical_name")

    class Meta:
        model = ProductAttribute
        fields = ("_canonicalName", "value")


class NutritionGroupAttributeImportSerializer(serializers.ModelSerializer):
    _canonicalName = serializers.CharField(source="canonical_name")

    class Meta:
        model = NutritionGroupAttribute
        fields = ("_canonicalName", "value")

class NutritionFactImportSerializer(serializers.ModelSerializer):
    _canonicalName = serializers.CharField(source="canonical_name")
    unitOfMeasure = serializers.CharField(source="unit_of_measure")

    class Meta:
        model = NutritionFact
        fields = ("_canonicalName", "unitOfMeasure", "amount")

class NutritionFactsGroupImportSerializer(serializers.ModelSerializer):
    nutritionGroupAttributes = serializers.SerializerMethodField(read_only=True, allow_null=True, required = False)
    nutritionFacts = serializers.SerializerMethodField(read_only=True, allow_null=True, required = False)

    def get_nutritionGroupAttributes(self, obj):
        nutrition = NutritionGroupAttribute.objects.using("eatfit").filter(nutrition_facts_group = obj)
        s = NutritionGroupAttributeImportSerializer(nutrition, many=True)
        return s.data

    def get_nutritionFacts(self, obj):
        nutrition = NutritionFact.objects.using("eatfit").filter(nutrition_facts_group = obj)
        s = NutritionFactImportSerializer(nutrition, many=True)
        return s.data

    class Meta:
        model = Nutrition
        fields = ("nutritionGroupAttributes", "nutritionFacts")

class NutritionAttributeImportSerializer(serializers.ModelSerializer):
    _canonicalName = serializers.CharField(source="canonical_name")
    _languageCode = serializers.CharField(source="language_code")

    class Meta:
        model = NutritionAttribute
        fields = ("_canonicalName", "value", "_languageCode")

class NutritionImportSerializer(serializers.ModelSerializer):
    nutritionFactsGroups = serializers.SerializerMethodField(read_only=True)
    nutritionAttributes = serializers.SerializerMethodField(read_only=True)

    def get_nutritionFactsGroups(self, obj):
        nutrition = NutritionFactsGroup.objects.using("eatfit").filter(nutrition = obj)[0]
        s = NutritionFactsGroupImportSerializer(nutrition)
        return s.data

    def get_nutritionAttributes(self, obj):
        nutrition = NutritionAttribute.objects.using("eatfit").filter(nutrition = obj)
        s = NutritionAttributeImportSerializer(nutrition, many=True)
        return s.data

    class Meta:
        model = Nutrition
        fields = ("nutritionFactsGroups", "nutritionAttributes")

class ProductImportSerializer(serializers.ModelSerializer):
    productNames = serializers.SerializerMethodField(read_only=True)
    productAttributes = serializers.SerializerMethodField(read_only=True)
    nutrition = serializers.SerializerMethodField(read_only=True)
    _gtin = serializers.CharField(source="gtin")
    main_category_id = serializers.IntegerField(source="nwd_main_category.pk")
    minor_category_id = serializers.CharField(source="nwd_subcategory.nwd_subcategory_id")

    def get_productNames(self, obj):
        product_names = ProductName.objects.using("eatfit").filter(product = obj)
        s = ProductNameImportSerializer(product_names, many=True)
        return s.data

    def get_productAttributes(self, obj):
        product_atts = ProductAttribute.objects.using("eatfit").filter(product = obj)
        s = ProductAttributeImportSerializer(product_atts, many=True)
        return s.data

    def get_nutrition(self, obj):
        nutrition = Nutrition.objects.using("eatfit").filter(product = obj)[0]
        s = NutritionImportSerializer(nutrition)
        return s.data

    class Meta:
        model = Product
        fields = ("_gtin", "main_category_id", "minor_category_id", "productNames", "productAttributes", "nutrition")

