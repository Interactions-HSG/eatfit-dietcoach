from NutritionService.serializers import ProductSerializer
import hashlib
import requests
import base64
import hmac


USER = 'autoidlabs2'
SECRET = '752DAB062D3E82189918234DF10D175E77DA07DF051FA324BBC8ADD543919DEC'  # Note it is in hex
BASE_URL = "http://www.codecheck.info/WebService/rest/"

def import_from_codecheck():
    mac, nonce = __authenticate()
    if mac and nonce:
        __get_product(123, mac, nonce)
    else:
        print("auth failed")

def __authenticate():
    data = {}
    data["authType"] = "DigestQuick"
    data["username"] = USER
    data["clientNonce"] = SECRET
    r = requests.post(BASE_URL + "session/auth", json=data)

    if r.status_code == requests.codes.ok:
        json_response = r.json()["result"]
        dig = hmac.new(USER, msg=USER.encode("utf-8") + base64.b64decode(json_response["nonce"]) + base64.b64decode(SECRET), digestmod=hashlib.sha256).digest()
        mac = base64.b64encode(dig).decode()  
        print(mac)
        return mac, json_response["nonce"]
    return None, None


def __get_product(gtin, mac, nonce):
    print("getting product")
    r = requests.get(BASE_URL + "prod/ean2/1/1/4006939082489", headers=__add_auth_header(mac, nonce))
    print(r.status_code)
    print(r.text)


def __add_auth_header(mac, nonce):
    auth_string = 'DigestQuick nonce="%s",mac="%s"' % (nonce, mac)
    return {'Authorization': auth_string}

