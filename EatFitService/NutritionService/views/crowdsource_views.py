# -*- coding: utf-8 -*-

"""
Definition of crowdsouce views.
"""

from rest_framework import permissions
from rest_framework.decorators import permission_classes
from NutritionService.models import CrowdsourceProduct
from NutritionService.serializers import CrowdsourceProductSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def create_crowdsouce_product(request):
    """
    Creates a new crowdsouce product. The 'name' field and the 'gtin' field are required to be in the request data.
    All other fields for the crowdsouce product are optional in this view.
    :param request: Request made by the user.
    :return: HTTP status code - 201 - A new entry was created and it is returned as JSON.
                              - 400 - There was an error when parsing the data or an entry exists with specified GTIN.
    """
    crowdsource_serializer = CrowdsourceProductSerializer(data=request.data)
    if crowdsource_serializer.is_valid():
        crowdsource_serializer.save()
        return Response(data=crowdsource_serializer.data, status=201)
    else:
        # Serializer was not valid. Note that if a crowdsouce product with this GTIN already exists, the
        # serializer would return an error: "Crowdsource Product with this GTIN already exists."
        return Response(crowdsource_serializer.errors, status=400)


@api_view(['PUT, GET'])
@permission_classes((permissions.IsAuthenticated,))
def handle_crowdsouce_product(request, gtin):
    if request.method == 'PUT':
        return __update_crowdsouce_product(request, gtin)
    elif request.method == 'GET':
        return __get_crowdsouce_product(request, gtin)
    else:
        # Method is not allowed
        return Response(status=405)


@api_view(['PUT'])
@permission_classes((permissions.IsAuthenticated,))
def __update_crowdsouce_product(request, gtin):
    crowdsource_serializer = CrowdsourceProductSerializer(data=request.data)
    if crowdsource_serializer.is_valid():
        try:
            crowdsource_product = CrowdsourceProduct.objects.get(gtin=gtin)
            # TODO: Update the product here
        except:
            # gtin was not found
            return Response(status=404)
        return Response(status=501)
    else:
        # Serializer was not valid.
        return Response(crowdsource_serializer.errors, status=400)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def __get_crowdsouce_product(request, gtin):
    crowdsouce_product = CrowdsourceProduct.object.get(gtin=gtin)
    return Response(status=501)


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def approve_crowdsouce_products(request):
    # Check permission of the user.
    # TODO: Create the permissions and then check for them here.
    return Response(status=501)
