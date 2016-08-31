from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes, parser_classes, renderer_classes
from TrustBoxAPI.serializer import ProductSerializer, ImportLogSerializer, ProductNameSerializer, ProductWithNameSerializer, ShoppingTipSerializer
from TrustBoxAPI.models import Product, ProductName, ImportLog, NwdSubcategory
from sets import Set
from TrustBoxAPI import tasks, category_handler, trustbox_connector
from EatFitService import settings
from rest_framework.parsers import FileUploadParser, FormParser
from django.db import connection
from rest_framework.renderers import JSONRenderer
from SaltTrackerService import result_calculation

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
@renderer_classes((JSONRenderer, ))
def product_by_name_like(request, name):
    cursor = connection.cursor()
    cursor.execute("Select top 50 n.name,a.value from product_name as n, product_attribute as a where n.language_code='de' and a.language_code='de' and a.canonical_name='productImageURL' and a.product_id=n.product_id and n.name like %s;", ["%" + name + "%"])
    rows = cursor.fetchall()
    #products = ProductName.objects.raw("Select top 50 n.* from product_name as n where n.language_code='de' and n.name like %s;", ["%" + name + "%"])
    #serializer = ProductWithNameSerializer(products, many=True)
    result = []
    for row in rows:
       result.append({"name" : row[0], "image_url" : row[1]})
    return Response(result)

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

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
@renderer_classes((JSONRenderer, ))
def get_shopping_tips(request, user_pk):
    products, tips = result_calculation.get_shopping_tips(user_pk)
    serializer = ShoppingTipSerializer(tips, many=True)
    result = {}
    result["products"] = products
    result["tips"] = serializer.data
    return Response(result)

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
@renderer_classes((JSONRenderer, ))
def get_icon_urls(request):
    names = request.data
    if names:
        icon_urls = NwdSubcategory.objects.filter(description__in=names).values_list("icon", flat=True)
        return Response(icon_urls)
    return Response(status = status.HTTP_400_BAD_REQUEST)
