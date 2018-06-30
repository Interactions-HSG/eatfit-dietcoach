from NutritionService.serializers import ProductSerializer
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

def import_from_codecheck():
    mac, nonce = __authenticate()
    if mac and nonce:
        return __get_product(123, mac, nonce)
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


def __get_product(gtin, mac, nonce):
    print("getting product")
    r = requests.get(BASE_URL + "prod/ean2/1/513/7610046004356", headers=__add_auth_header(mac, nonce))
    """
    if r.status_code == 200:
        response_data = r.json()["result"]
        product = Product()
        product.gtin = response_data["ean"]

        product.save()

        Ingredient.objects.update_or_create(product = product, lang = "de", defaults = {"text" : unicode(response_data["ingr"])})
    """
    print(r.status_code)
    return r.json()


def __add_auth_header(mac, nonce):
    auth_string = 'DigestQuick nonce="%s",mac="%s"' % (nonce, mac)
    return {'Authorization': auth_string}

