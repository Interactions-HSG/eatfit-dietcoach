from rest_framework import serializers


class ReebateItemSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    quantity = serializers.FloatField()
    price = serializers.FloatField()
    currency = serializers.CharField()

class ReebateReceiptSerializer(serializers.Serializer):
    id = serializers.CharField()
    externalId = serializers.CharField()
    dateOfPurchaseInMillis = serializers.FloatField()
    timezoneId = serializers.CharField()
    store = serializers.CharField()
    lineItems = ReebateItemSerializer(many=True)

class ReebateSerializer(serializers.Serializer):
    message = serializers.CharField()
    receipts = ReebateReceiptSerializer(many=True, required=False, allow_null=True)
    enabled = serializers.BooleanField()
    authenticated = serializers.BooleanField()
