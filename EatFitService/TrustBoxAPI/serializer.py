from rest_framework import serializers
from TrustBoxAPI.models import Product, ImportLog, ProductName

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
