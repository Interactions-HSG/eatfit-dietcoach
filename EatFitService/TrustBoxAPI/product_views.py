from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes, parser_classes
from TrustBoxAPI.serializer import ProductSerializer, ImportLogSerializer, ProductNameSerializer
from TrustBoxAPI.models import Product, ProductName, ImportLog
from sets import Set
from TrustBoxAPI import tasks, category_handler, trustbox_connector
from EatFitService import settings
from rest_framework.parsers import FileUploadParser, FormParser

@permission_classes((permissions.IsAuthenticated,))
class ProductViewSet(viewsets.ViewSet):

    def list(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def create(self, request):
        return Response(status = status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, pk=None):
        product = Product.objects.get(pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def update(self, request, pk=None):
        return Response(status = status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, pk=None):
        return Response(status = status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def product_by_gtin(request, gtin):
    product = get_object_or_404(Product.objects.all(), gtin = gtin)
    serializer = ProductSerializer(product)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def product_by_name(request, name):
    names = ProductName.objects.filter(name = name)
    products = Set()
    for name in names:
        products.add(Product.objects.get(pk=name.product.pk))
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def names_of_product(request, product_pk):
    names = ProductName.objects.filter(product=product_pk)
    serializer = ProductNameSerializer(names, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def import_log_all(request):
    logs = ImportLog.objects.all()
    serializer = ImportLogSerializer(logs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def import_log_latest(request):
    log = ImportLog.objects.latest("import_timestamp")
    serializer = ImportLogSerializer(log)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def import_data(request):
    tasks.get_trustbox_data_by_call.delay()
    return Response(status = status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def import_categories(request):
    category_handler.import_categories()
    return Response(status = status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def map_categories(request, iteration):
    tasks.map_categories_to_gtin.delay(iteration)
    return Response(status = status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def export_unmapped_products(request):
    category_handler.export_unmapped_products()
    return Response(status = status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_product_from_trustbox(request, gtin):
    trustbox_product = trustbox_connector.get_single_product(gtin)
    return Response(trustbox_product)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def product_from_trustbox_in_db(request, gtin):
    trustbox_connector.single_product_to_db(gtin)
    return Response(status = status.HTTP_200_OK)

