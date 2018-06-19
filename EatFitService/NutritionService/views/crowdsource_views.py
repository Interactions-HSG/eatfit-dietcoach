# -*- coding: utf-8 -*-

"""
Definition of crowdsouce views.
"""

from rest_framework import permissions
from rest_framework.decorators import permission_classes, parser_classes
from rest_framework.parsers import FormParser, MultiPartParser, FileUploadParser, JSONParser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from NutritionService.models import CrowdsourceProduct, Product, NutritionFact, Ingredient
from NutritionService.serializers import CrowdsourceProductSerializer, ProductSerializer
from NutritionService import helpers


GRAM = 'g'
KJ = 'KJ'

"""
These values are used for creating nutrients for the products. 
    1. 'name': This is used as the value for the name column in the NutrientFact model.
    2. 'unit_of_measure': This is used for the value or the unit_of_measure column in the NutrientFact model.
    3. 'db_column_name': This is used to get the name of the crowdsource product db column name, e.g. salt.
"""
SALT = {'name': 'salt', 'unit_of_measure': GRAM, 'db_column_name': 'salt'}
SODIUM = {'name': 'sodium', 'unit_of_measure': GRAM, 'db_column_name': 'sodium'}
ENERGY_KJ = {'name': 'energyKJ', 'unit_of_measure': KJ, 'db_column_name': 'energy'}
TOTAL_FAT = {'name': 'totalFat', 'unit_of_measure': GRAM, 'db_column_name': 'fat'}
SATURATED_FAT = {'name': 'saturatedFat', 'unit_of_measure': GRAM, 'db_column_name': 'saturated_fat'}
TOTAL_CARBS = {'name': 'totalCarbohydrate', 'unit_of_measure': GRAM, 'db_column_name': 'carbohydrate'}
SUGARS = {'name': 'sugars', 'unit_of_measure': GRAM, 'db_column_name': 'sugar'}
FIBER = {'name': 'dietaryFiber', 'unit_of_measure': GRAM, 'db_column_name': 'fibers'}
PROTEIN = {'name': 'protein', 'unit_of_measure': GRAM, 'db_column_name': 'protein'}

NUTRITION_LIST = [SALT, SODIUM, ENERGY_KJ, TOTAL_FAT, SATURATED_FAT, TOTAL_CARBS, SUGARS, FIBER, PROTEIN]

# Used for error handling
EMPTY_INPUT = 'Empty input!'
INVALID_INPUT = 'The input is invalid format!'
ERROR_CREATING = 'There was an error when creating the products!'


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
@parser_classes((MultiPartParser,))
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


@api_view(['GET', 'PUT'])
@permission_classes((permissions.IsAuthenticated,))
@parser_classes((MultiPartParser,))
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
@parser_classes((MultiPartParser,))
def __update_crowdsouce_product(request, gtin):
    request.data['gtin'] = gtin
    try:
        crowdsource_product = CrowdsourceProduct.objects.get(gtin=gtin)
    except:
        # gtin was not found
        return Response(status=404)

    crowdsource_serializer = CrowdsourceProductSerializer(crowdsource_product, data=request.data, partial=True)
    if crowdsource_serializer.is_valid():
        # Save the new changes to the crowdsource product.
        crowdsource_serializer.save()
        return Response(crowdsource_serializer.data, status=200)
    else:
        # Serializer was not valid.
        return Response(crowdsource_serializer.errors, status=400)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def __get_crowdsouce_product(request, gtin):
    try:
        crowdsouce_product = CrowdsourceProduct.objects.get(gtin=gtin)
    except:
        # The crowdsource product with the specified GTIN was not found.
        return Response('Crowdsource product not found', status=404)
    return Response(data=CrowdsourceProductSerializer(crowdsouce_product).data, status=200)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_all_crowdsource_products(request):
    crowdsource_products = CrowdsourceProduct.objects.all()
    if crowdsource_products.exists():
        return Response(data=CrowdsourceProductSerializer(crowdsource_products, many=True).data, status=200)
    else:
        return Response(status=404)


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def approve_crowdsouce_products(request):
    """
    Approves given crowdsource products to move them to the product table. They are specified by a list of
    gtins of crowdsource products passed in the request data.
    Example request: POST /crowdsource/approve/
                     request data: {"gtins":["7610046004356", "48746874521687"]}
    """
    # Only superusers are allowed to approve crowdsouce products.
    if not request.user.is_superuser:
        return Response(status=403)

    try:
        gtins = request.data['gtins']
    except KeyError:
        return Response('Array of GTINs was missing from the request data! '
                        'Name of the key for array should be "gtins".', status=400)

    # Get all the available crowdsource products with the specified gtins.
    crowdsource_products = CrowdsourceProduct.objects.filter(gtin__in=gtins)
    if not crowdsource_products.exists():
        return Response('No crowdsource records were found for the specified GTINs.',
                        status=404)
    success, result, invalid_gtins = __create_products_from_crowdsource(list(crowdsource_products.all()))
    # Validate the products were created successfully.
    if not success:
        if len(invalid_gtins) != 0:
            return Response({'error': 'The specified GTINs are not valid to be turned into products!',
                             'gtins': invalid_gtins}, status=400)
        return Response('There was en error creating the products!', status=400)

    # Return all the created products. Note that the returned products here are of type Product, not CrowdsourceProduct.
    return_data = {'products:': ProductSerializer(result, many=True).data,
                   'invalid_gtins': invalid_gtins}
    return Response(data=return_data, status=201)


def __create_products_from_crowdsource(crowdsource_products):
    # Make sure the input is valid.
    if crowdsource_products is None:
        return False, EMPTY_INPUT, None

    # Check if the input is a list.
    if not isinstance(crowdsource_products, list):
        return False, INVALID_INPUT, None

    # Check if all elements of the input are of type CrowdsourceProduct.
    if not all(isinstance(element, CrowdsourceProduct) for element in crowdsource_products):
        return False, INVALID_INPUT, INVALID_INPUT

    created_products = []
    invalid_gtins = []
    # Create a new Product entry for every crowdsource product available.
    for crowdsource_product in crowdsource_products:

        # TODO: What about product's allergens

        is_crowdsource_product_valid, errors = __validate_crowdsource_product(crowdsource_product)
        if not is_crowdsource_product_valid:
            # The specified crowdsource product was not valid for creating a new product, so we add it
            # to the list of invalid gtins and continue with the next one.
            invalid_gtins.append({'gtin': crowdsource_product.gtin, 'errors': errors})
            continue

        product = Product()
        product.gtin = crowdsource_product.gtin
        product.source = Product.CROWDSOURCING
        product.source_checked = False
        product.product_name_en = crowdsource_product.product_name_en
        product.product_name_de = crowdsource_product.product_name_de
        product.product_name_it = crowdsource_product.product_name_it
        product.product_name_fr = crowdsource_product.product_name_fr
        product.image = crowdsource_product.front_image
        product.back_image = crowdsource_product.back_image
        product.comment = crowdsource_product.comment
        product.major_category = crowdsource_product.major_category
        product.minor_category = crowdsource_product.minor_category
        product.producer = crowdsource_product.producer
        product.product_size = crowdsource_product.product_size
        product.product_size_unit_of_measure = crowdsource_product.product_size_unit_of_measure
        product.serving_size = crowdsource_product.serving_size
        product.created = crowdsource_product.created
        product.updated = crowdsource_product.updated
        # Save the product in order to get an entry in the DB so we can insert the nutrition facts using the
        # product's ID as a foreign key for the nutrition facts.
        product.save()

        # When a new crowdsource product was created, the values MUST have been specified per 100g/ml.
        nutrition_facts_to_create = []
        for nutrition in NUTRITION_LIST:
            # Check if there is a nutrition for every available name.
            # Note that there MUST be - see __validate_crowdsource_product(crowdsource_product)
            if crowdsource_product[nutrition['db_column_name']]:
                nutrition_facts_to_create.append(NutritionFact(product=product,
                                                               name=nutrition['name'],
                                                               amount=crowdsource_product[nutrition['db_column_name']],
                                                               unit_of_measure=nutrition['unit_of_measure']
                                                               ))

        # Check if there are nutrition facts to create.
        if len(nutrition_facts_to_create) != 0:
            NutritionFact.objects.bulk_create(nutrition_facts_to_create)

        # Create ingredients entries for the product.
        ingredients_to_create = []
        if crowdsource_product.ingredient_en:
            ingredients_to_create.append(Ingredient(product=product, lang='en', text=crowdsource_product.ingredient_en))
        if crowdsource_product.ingredient_de:
            ingredients_to_create.append(Ingredient(product=product, lang='de', text=crowdsource_product.ingredient_de))
        if crowdsource_product.ingredient_fr:
            ingredients_to_create.append(Ingredient(product=product, lang='fr', text=crowdsource_product.ingredient_fr))
        if crowdsource_product.ingredient_it:
            ingredients_to_create.append(Ingredient(product=product, lang='it', text=crowdsource_product.ingredient_it))

        # Check if there are ingredients to create.
        if len(ingredients_to_create) != 0:
            Ingredient.objects.bulk_create(ingredients_to_create)

        # Based on the inserted nutrition facts calculate the product's ofcom value and save it to the entry.
        # Note that in the function the product is saved.
        helpers.calculate_ofcom_value(product)

        # Add the product to the list of created products which will be returned as data from this function.
        created_products.append(product)

    if len(created_products) != 0:
        # At least one product was created so we return the result. Note that if some of the specified
        # gtins were not created, they are also returned to the user.
        created_products_gtins = [product.gtin for product in created_products]
        __delete_crowdsource_products(created_products_gtins)
        return True, created_products, invalid_gtins
    elif len(invalid_gtins) != 0:
        # No products were created, but all the gtins are invalid so we return them.
        return False, ERROR_CREATING, invalid_gtins
    else:
        return False, ERROR_CREATING, ERROR_CREATING


def __validate_crowdsource_product(crowdsource_product):
    errors = []
    # Make sure there are ALL the nutrition facts.
    for nutrition in NUTRITION_LIST:
        if not crowdsource_product[nutrition['db_column_name']]:
            errors.append('Missing: ' + nutrition['name'])
    if not crowdsource_product.name:
        errors.append('Missing product name')
    if not crowdsource_product.gtin:
        errors.append('Missing product gtin')
    if not crowdsource_product.product_name_en:
        errors.append('Missing product en name')
    if not crowdsource_product.product_name_de:
        errors.append('Missing product de name')
    if not crowdsource_product.product_name_it:
        errors.append('Missing product it name')
    if not crowdsource_product.product_name_fr:
        errors.append('Missing product fr name')
    existing_products = Product.objects.filter(gtin = crowdsource_product.gtin)
    if existing_products.exist():
        errors.append('Product with this GTIN already exists')
    """
    if not crowdsource_product.ingredient_en:
        errors.append('Missing product en ingredients')
    if not crowdsource_product.ingredient_de:
        errors.append('Missing product de ingredients')
    if not crowdsource_product.ingredient_fr:
        errors.append('Missing product fr ingredients')
    if not crowdsource_product.ingredient_it:
        errors.append('Missing product it ingredients')
    """
    # If there are errors, the crowdsource product is NOT valid so False is returned including the errors.
    if len(errors) != 0:
        return False, errors
    # Else there are no errors so the crowdsource product is valid.
    return True, None


def __delete_crowdsource_products(created_products_gtins):
    CrowdsourceProduct.objects.filter(gtin__in=created_products_gtins).delete()
