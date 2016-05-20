
from EatFitService import settings
import xlrd
from xlrd.sheet import ctype_text
from TrustBoxAPI.models import NwdMainCategory, NwdSubcategory, Product

MAPPING_V1 = "Trustbox_Produkte_kategorisiert_v1.xlsx"
CATEGORIES = "Categories_NWD.xlsx"

def import_categories():
    path = settings.BASE_DIR + "/TrustBoxAPI/static/category/" + CATEGORIES
    book = xlrd.open_workbook(path)
    sh = book.sheet_by_index(0)
    i = 0
    main_category = None
    for rx in range(sh.nrows):
        if i < 1: #first line is excel header
            pass
        else:
            nwd_id = sh.row(rx)[0]
            nwd_description = sh.row(rx)[1]
            if isint(nwd_id.value):
                current_main = nwd_id.value
                main_category, created = NwdMainCategory.objects.update_or_create(
                    nwd_main_category_id=nwd_id.value,
                    defaults={'description':nwd_description.value})
            else:
                if main_category != None:
                    sub_category, created = NwdSubcategory.objects.update_or_create(
                        nwd_subcategory_id=nwd_id.value, 
                        defaults={'description':nwd_description.value, "nwd_main_category" : main_category})
        i = i+1

def map_categories():
    path = settings.BASE_DIR + "/TrustBoxAPI/static/category/" + MAPPING_V1
    book = xlrd.open_workbook(path)
    sh = book.sheet_by_index(0)
    i = 0
    main_category = None
    for rx in range(sh.nrows):
        if i < 1: #first line is excel header
            pass
        else:
            try:
                gtin = sh.row(rx)[0]
                nwd_sub_id = sh.row(rx)[5]
                sub_categories = NwdSubcategory.objects.filter(nwd_subcategory_id = str(nwd_sub_id.value))
                if sub_categories.exists():
                    products = Product.objects.filter(gtin = int(gtin.value))
                    if products.exists():
                        product = products[0]
                        product.nwd_main_category = sub_categories[0].nwd_main_category
                        product.nwd_subcategory = sub_categories[0]
                        product.save()
                else:
                    categories = NwdMainCategory.objects.filter(nwd_main_category_id = int(nwd_sub_id.value))
                    if categories.exists():
                       products = Product.objects.filter(gtin = int(gtin.value))
                       if products.exists():
                        product = products[0]
                        product.nwd_main_category = categories[0]
                        product.save()
            except Exception as e:
                print(str(e))
        i = i+1
    print("mapped: " + str(i) + " categories to gtin") 

def isint(x):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b


