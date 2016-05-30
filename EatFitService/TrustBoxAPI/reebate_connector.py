import requests
from EatFitService import settings
import xlrd
from TrustBoxAPI.models import ProductName

def get_customer_trace():
    data = {'username':settings.REEBATE_USERNAME, "password": settings.REEBATE_PASSWORD, "lastReceiptMillis" : 1444216910000} 
    r = requests.post(settings.REEBATE_URL, data=data)
    print(r.text)


def excel_trace_to_db():
    book = xlrd.open_workbook("E:\\Dropbox\\Projekt Salz\\0 Technical\\Reebate\\Klaus_Migros-Cumulus_Log.xls")
    sh = book.sheet_by_index(0)
    matches = 0
    for rx in range(sh.nrows):
        if i < 1: #first line is excel header
            pass
        else:
            article_name = sh.row(rx)[5]
            product_names = ProductName.objects.filter(language_code="de", name=article_name)
            if product_names.exists():
                print(product_name.name)
                matches = matches + 1
    print("# of matches: " + str(matches))