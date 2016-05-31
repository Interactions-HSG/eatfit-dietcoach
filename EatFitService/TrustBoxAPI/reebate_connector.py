import requests
from EatFitService import settings
import xlrd
from TrustBoxAPI.models import ProductName
from fuzzywuzzy import fuzz

def get_customer_trace():
    data = {'username':settings.REEBATE_USERNAME, "password": settings.REEBATE_PASSWORD, "lastReceiptMillis" : 1444216910000} 
    r = requests.post(settings.REEBATE_URL, data=data)
    print(r.text)


def excel_trace_to_db():
    book = xlrd.open_workbook("E:\\Dropbox\\Projekt Salz\\0 Technical\\Reebate\\Klaus_Migros-Cumulus_Log.xls")
    sh = book.sheet_by_index(0)
    matches = 0
    product_names = ProductName.objects.filter(language_code="de")
    for rx in range(sh.nrows):
        if rx < 1: #first line is excel header
            pass
        else:
            article_name = sh.row(rx)[5]
            for product_name in product_names:
                r = fuzz.token_set_ratio(product_name.name, article_name)
                if r > 80:
                    print("product name: " + str(product_name.name) + " article name: " + str(article_name))
                    matches = matches + 1
    print("# of matches: " + str(matches))