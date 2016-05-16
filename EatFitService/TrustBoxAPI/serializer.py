from rest_framework import serializers
from TrustBoxAPI.models import Product, ImportLog

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ImportLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportLog
        fields = '__all__'
