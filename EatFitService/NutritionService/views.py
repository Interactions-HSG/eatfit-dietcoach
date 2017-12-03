"""
Definition of views.
"""

from EatFitService.settings import TRUSTBOX_USERNAME, TRUSTBOX_PASSWORD, TRUSTBOX_URL
from datetime import datetime
from NutritionService.models import ImportLog
from suds.client import Client
from suds.sudsobject import asdict
from django.http import HttpResponse
from NutritionService.models import Product, Allergen, Ingridient, NutritionFact, NotFoundLog
from NutritionService.serializers import ProductSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
import tempfile
from django.core import files
import random
import string


@api_view(['GET'])
def get_product(req, gtin):
    """
    Get product information given gtin
    returns sucess and object

    """
    products = Product.objects.filter(gtin=gtin)
    if not products.exists():
        l, created = NotFoundLog.objects.get_or_create(gtin=gtin)
        if not created:
            l.count = l.count + 1
            l.save()
        result = {}
        result["success"] = False
        result["products"] = None
        return Response(result)
    else:
        serializer = ProductSerializer(products, many=True)
        result = {}
        result["success"] = True
        result["products"] = serializer.data
    return Response(result)


def update_database(req):
    """ checks for changes since last update and adds new objects"""
    last_updated='2000-01-01T00:00:00Z'
    import_log_queryset = ImportLog.objects.filter(import_finished__isnull=False).order_by("-import_finished")[:1]
    if import_log_queryset.exists():
        last_updated = import_log_queryset[0].import_finished.strftime("%Y-%m-%dT%H:%M:%SZ")
    __update_objects_from_trustbox(last_updated)
    return HttpResponse(status = 200)


def __update_objects_from_trustbox(last_updated):
    """
    Takes date of last updated and creates new and changed objects
    """
    client = Client(TRUSTBOX_URL)
    response = client.service.getChangedArticles(last_updated, TRUSTBOX_USERNAME, TRUSTBOX_PASSWORD)
    updated_gtins = [article['gtin'] for article in __recursive_translation(response)["article"]]
    import_log = ImportLog.objects.create(import_started = datetime.now())
    count = 0
    for gtin in updated_gtins[:10]:
        count = count + 1
        result = client.service.getTrustedDataByGTIN(gtin, TRUSTBOX_USERNAME, TRUSTBOX_PASSWORD)
        __soap_response_to_objects(result)
        print("imported model: " + str(count))
    import_log.import_finished = datetime.now()
    import_log.save()

# to be optimized -- objects can be created in batches 
def __soap_response_to_objects(response):
    """
    Takes SOAP response from TRUSTBOX, crates and save object in DB.
    Create Object and save in same method due to fg-keys constraints.
    """
    result_as_dict = __recursive_translation(response)
    products = result_as_dict['productList'][0]['products']
    for p in products:
        try:
            temp_image_url = None
            filter_arguments = {}
            for n in p['productNames']:
                if n['_languageCode'] == "de":
                    filter_arguments["product_name_de"] = n['name']
                if n['_languageCode'] == "fr":
                    filter_arguments["product_name_fr"] = n['name']
                if n['_languageCode'] == "en":
                    filter_arguments["product_name_en"] = n['name']
                if n['_languageCode'] == "it":
                    filter_arguments["product_name_it"] = n['name']
            for attr in p['productAttributes']:
                try:
                    if attr['_canonicalName'] == 'manufacturer':
                        filter_arguments["producer"] = attr['value']
                    if attr['_canonicalName'] == 'packageSize':
                        filter_arguments["product_size"] = attr['value']
                    if attr['_canonicalName'] == 'packageSize_uom':
                        filter_arguments["product_size_unit_of_measure"] = attr['value']
                    if attr['_canonicalName'] == 'productImageURL':
                        temp_image_url = attr['value']
                except:
                    continue
            if 'nutritionGroupAttributes' in p['nutrition']['nutritionFactsGroups']:
                for attr in p['nutrition']['nutritionFactsGroups']['nutritionGroupAttributes']:
                    if attr['_canonicalName'] == 'servingSize' and attr['value'] != "0.0": 
                        #check against 0 due to multiple entries with different values
                        filter_arguments["serving_size"] = attr['value']

            product, created = Product.objects.update_or_create(defaults={'gtin': p['_gtin']},**filter_arguments)
            if temp_image_url:
                __store_image(temp_image_url, product)

            # create nutrition facts for products
            if 'nutritionFacts' in p['nutrition']['nutritionFactsGroups']:
                for attr in p['nutrition']['nutritionFactsGroups']['nutritionFacts']:
                    try:
                        is_a_number, number = is_number(attr['amount'])
                        if is_a_number:
                            filter_arguments = {}
                            filter_arguments["amount"] = number 
                            filter_arguments["unit_of_measure"] = attr['unitOfMeasure'] 
                            NutritionFact.objects.update_or_create(defaults= {"product" : product, "name" : attr["_canonicalName"]}, **filter_arguments)
                    except: #ignore shitty data quality
                        continue
        
            # create allergens and ingridients for products
            for attr in p['nutrition']['nutritionAttributes']:
                if attr['_canonicalName'].startswith('allergen') and attr['value'] != "false":
                    Allergen.objects.update_or_create(defaults= {"product" : product, "name" : attr["_canonicalName"]}, **{"certainity" : attr['value']})
                if attr['_canonicalName'] == 'ingredients':
                    Ingridient.objects.update_or_create(defaults= {"product" : product, "lang" : attr["_languageCode"]}, **{"text" : attr['value']})
        except:
            continue

def __recursive_translation(d):
    ### helper method to translate SOAP response to dictionary ###
    result = {}
    for k, v in asdict(d).iteritems():
        if hasattr(v, '__keylist__'):
            result[k] = __recursive_translation(v)
        elif isinstance(v, list):
            result[k] = []
            for item in v:
                if hasattr(item, '__keylist__'):
                    result[k].append(__recursive_translation(item))
                else:
                    result[k].append(item)
        else:
            result[k] = v
    return result


def __store_image(image_url, product):
    if product.original_image_url == None or product.original_image_url != image_url:
        try:
            request = requests.get(image_url, stream=True)
            # Was the request OK?
            if request.status_code != requests.codes.ok:
                return

            # Get the filename from the url, used for saving later
            file_name = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20)) + ".jpg"

            # Create a temporary file
            lf = tempfile.NamedTemporaryFile()

            # Read the streamed image in sections
            for block in request.iter_content(1024 * 8):

                # If no more file then stop
                if not block:
                    break

                # Write image block to temporary file
                lf.write(block)

            # Save the temporary image to the model#
            # This saves the model so be sure that is it valid
            product.image.save(file_name, files.File(lf))
        except Exception as ex:
            print(ex)


def is_number(s):
    try:
        v = float(s)
        return True, v 
    except ValueError:
        return False, None