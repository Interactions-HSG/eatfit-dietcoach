from NutritionService.serializers import ProductSerializer
import hashlib
import requests
import base64


USER = 'autoidlabs2'
SECRET = '752DAB062D3E82189918234DF10D175E77DA07DF051FA324BBC8ADD543919DEC'  # Note it is in hex
BASE_URL = "http://www.codecheck.info/WebService/rest/"

def import_from_codecheck():
    __authenticate()

def __authenticate():
    data = {}
    data["authType"] = "DigestQuick"
    data["username"] = USER
    data["clientNonce"] = SECRET
    r = requests.post(BASE_URL + "session/auth", json=data)

    if r.status_code == requests.codes.ok:
        json_response = r.json()["result"]
        mac = hashlib.sha256(USER.encode() + base64.b64decode(json_response["nonce"]) + base64.b64decode(SECRET)).hexdigest()
        print(mac)


def search_for_gtins(gtins):
    created_products, not_found_gtins = __import_products(gtins)
    return {'products': ProductSerializer(created_products, many=True).data,
            'not_found_gtins': not_found_gtins}


def __import_products(gtins):
    return [], []
