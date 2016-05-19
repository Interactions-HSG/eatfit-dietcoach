import requests
from EatFitService import settings


def get_customer_trace():
    data = {'username':settings.REEBATE_USERNAME, "password": settings.REEBATE_PASSWORD, "lastReceiptMillis" : 1444216910000} 
    r = requests.post(settings.REEBATE_URL, data=data)