import requests
from EatFitService import settings
import xlrd
from TrustBoxAPI.models import ProductName
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

def get_customer_trace():
    data = {'username':settings.REEBATE_USERNAME, "password": settings.REEBATE_PASSWORD, "lastReceiptMillis" : 1444216910000} 
    r = requests.post(settings.REEBATE_URL, data=data)
    print(r.text)


def excel_trace_to_db():
    book = xlrd.open_workbook("E:\\Dropbox\\Projekt Salz\\0 Technical\\Reebate\\Klaus_Migros-Cumulus_Log.xls")
    sh = book.sheet_by_index(0)
    matches = 0
    product_names = ProductName.objects.filter(language_code="de")
    reebate_article_names = {}
    choices = [p.name for p in product_names]
    i = 0
    for rx in range(sh.nrows):
        if rx < 1: #first line is excel header
            pass
        else:
            article_name = str(sh.row(rx)[5]).encode("utf8")
            if not article_name in reebate_article_names:
                i = i+ 1
                print("processing new article_name: " + str(i))
                reebate_article_names[article_name] = ""
                best_fitting_product_name_score = 0
                for product_name in product_names:
                    r = fuzz.token_set_ratio(product_name.name.encode("utf8"), article_name)
                    if r > 70:
                        if r > best_fitting_product_name_score:
                            reebate_article_names[article_name] = product_name.name.encode("utf8")
                            best_fitting_product_name_score = r 
                        matches = matches + 1
    print("# of matches: " + str(sum(1 if reebate_article_names[r] != "" else 0 for r in reebate_article_names)))
    i = 0
    f = open("matching.txt", "w+")
    for k in reebate_article_names:
        f.write(k + " , " + reebate_article_names[k] + "\n")
        i = i+ 1
    f.close() 