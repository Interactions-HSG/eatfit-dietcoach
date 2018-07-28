from NutritionService.serializers import ProductSerializer
from NutritionService.models import NotFoundLog
from NutritionService.helpers import store_image
from NutritionService.models import NutritionFact
from NutritionService.models import Ingredient
from NutritionService.models import Product
import base64
import binascii
import hashlib
import hmac
import json
import os
import requests


USER = 'autoidlabs2'
SECRET = '752DAB062D3E82189918234DF10D175E77DA07DF051FA324BBC8ADD543919DEC'  # Note it is in hex
BASE_URL = "http://www.codecheck.info/WebService/rest/"
GRAM = "g"

def import_from_codecheck():
    mac, nonce = __authenticate()
    if mac and nonce:
        items_found = __get_products(mac, nonce)
        if len(items_found) > 0:
            NotFoundLog.objects.filter(gtin__in=items_found).delete()
    else:
        print("auth failed")

def __authenticate():
    client_nonce_data = os.urandom(16)

    login_info = {
	    'authType': 'DigestQuick',
	    'username': USER,
	    'clientNonce': base64.b64encode(client_nonce_data),
    }
    r = requests.post(BASE_URL + "session/auth", json=login_info)

    if r.status_code == requests.codes.ok:
        json_response = r.json()["result"]
        username_data = USER  # is already in UTF-8 as it's ASCII
        nonce_data = base64.b64decode(json_response['nonce'])
        mergedBytes = username_data + nonce_data + client_nonce_data
        encoded_mac = base64.b64encode(hmac.new(binascii.a2b_hex(SECRET), msg=mergedBytes, digestmod=hashlib.sha256).digest())
        return encoded_mac, json_response['nonce']
    return None, None


def __get_products(mac, nonce):
    not_found_items = NotFoundLog.objects.filter(processed = False)
    items_found = []
    for not_found_item in not_found_items:
        try:
            gtin = str(not_found_item.gtin)
            r = requests.get(BASE_URL + "prod/ean2/1/513/" + str(gtin), headers=__add_auth_header(mac, nonce))
            if r.status_code == 200:
                response_data = r.json()["result"]
                items_found.append(response_data["ean"])
                product = Product()
                product.gtin = response_data["ean"]
                product.source = Product.CODECHECK
                if "name" in response_data:
                    product.product_name_de = response_data["name"]
                if "manu" in response_data:
                    product.producer = response_data["manu"]

                product.save()

                if "imgUrl" in response_data:
                    store_image(response_data["imgUrl"], product)
                elif "imgId" in response_data:
                    store_image(BASE_URL + "img/id/" + response_data["imgId"] + "/1", product)

                if "ingr" in response_data:
                    Ingredient.objects.update_or_create(product = product, lang = "de", defaults = {"text" : unicode(response_data["ingr"])})
        
                if "nutriTable" in response_data:
                    nutrient_table = response_data["nutriTable"]
                    nutrition_facts_to_create = []
                    if "salt" in nutrient_table:
                        nutrition_fact1 = NutritionFact(product = product, name = "salt", amount = nutrient_table["salt"], unit_of_measure = GRAM)
                        nutrition_facts_to_create.append(nutrition_fact1)

                    if "calories" in nutrient_table:
                        nutrition_fact3 = NutritionFact(product = product, name = "energyKcal", amount = nutrient_table["calories"], unit_of_measure = "Kcal")
                        nutrition_facts_to_create.append(nutrition_fact3)
                
                    if "energy" in nutrient_table:
                        nutrition_fact3 = NutritionFact(product = product, name = "energyKJ", amount = nutrient_table["energy"], unit_of_measure = "KJ")
                        nutrition_facts_to_create.append(nutrition_fact3)

                    if "fat" in nutrient_table:
                        nutrition_fact4 = NutritionFact(product = product, name = "totalFat", amount = nutrient_table["fat"], unit_of_measure = GRAM)
                        nutrition_facts_to_create.append(nutrition_fact4)

                    if "saturatedFat" in nutrient_table:
                        nutrition_fact5 = NutritionFact(product = product, name = "saturatedFat", amount = nutrient_table["saturatedFat"], unit_of_measure = GRAM)
                        nutrition_facts_to_create.append(nutrition_fact5)

                    if "carbonhydrates" in nutrient_table:
                        nutrition_fact6 = NutritionFact(product = product, name = "totalCarbohydrate", amount = nutrient_table["carbonhydrates"], unit_of_measure = GRAM)
                        nutrition_facts_to_create.append(nutrition_fact6)

                    if "sugar" in nutrient_table:
                        nutrition_fact7 = NutritionFact(product = product, name = "sugars", amount = nutrient_table["sugar"], unit_of_measure = GRAM)
                        nutrition_facts_to_create.append(nutrition_fact7)

                    if "fibers" in nutrient_table:
                        nutrition_fact8 = NutritionFact(product = product, name = "dietaryFiber", amount = nutrient_table["fibers"], unit_of_measure = nutrients["fiber"]["unit"])
                        nutrition_facts_to_create.append(nutrition_fact8)

                    if "protein" in nutrient_table:
                        nutrition_fact9 = NutritionFact(product = product, name = "protein", amount = nutrient_table["protein"], unit_of_measure = nutrients["protein"]["unit"])
                        nutrition_facts_to_create.append(nutrition_fact9)

                    if "sodium" in nutrient_table:
                        nutrition_fact9 = NutritionFact(product = product, name = "sodium", amount = nutrient_table["sodium"], unit_of_measure = nutrients["protein"]["unit"])
                        nutrition_facts_to_create.append(nutrition_fact9)

                    NutritionFact.objects.bulk_create(nutrition_facts_to_create)
                    calculate_ofcom_value(product)
        except Exception as e:
            print(e)
    return items_found


def __add_auth_header(mac, nonce):
    auth_string = 'DigestQuick nonce="%s",mac="%s"' % (nonce, mac)
    return {'Authorization': auth_string}

