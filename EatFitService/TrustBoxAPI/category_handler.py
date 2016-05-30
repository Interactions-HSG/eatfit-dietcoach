
from EatFitService import settings
import xlwt, xlrd
from xlutils.copy import copy
from xlrd.sheet import ctype_text
from django.db.models import Q
from TrustBoxAPI.models import NwdMainCategory, NwdSubcategory, Product, ProductName, NutritionFact, NutritionAttribute, ProductAttribute

MAPPING_FILE_NAME = "Trustbox_Produkte_kategorisiert_v"
CATEGORIES = "Categories_NWD.xlsx"
BLANK_FILE_NAME = "Trustbox_Produkte_blank.xls"
UNCATEGORISED_FILE_NAME = "Trustbox_Produkte_nicht_kategorisiert.xls"

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

def map_categories(iteration):
    path = settings.BASE_DIR + "/TrustBoxAPI/static/category/" + MAPPING_FILE_NAME + str(iteration) + ".xlsx"
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
    
def export_unmapped_products():
    path = settings.BASE_DIR + "/TrustBoxAPI/static/category/" + BLANK_FILE_NAME
    r_book = xlrd.open_workbook(path, formatting_info=True)
    r_sheet = r_book.sheet_by_index(0)
    workbook = copy(r_book)
    w_sheet = workbook.get_sheet(0)

    xlwt.add_palette_colour("kcal_color", 0x21)
    xlwt.add_palette_colour("fat_color", 0x22)
    xlwt.add_palette_colour("carbonate_color", 0x23)
    xlwt.add_palette_colour("protein_color", 0x24)
    xlwt.add_palette_colour("salt_color", 0x25)
    workbook.set_colour_RGB(0x21, 204,255,255)
    workbook.set_colour_RGB(0x22, 255,255,204)
    workbook.set_colour_RGB(0x23, 204,255,204)
    workbook.set_colour_RGB(0x24, 255,204,204)
    workbook.set_colour_RGB(0x25, 204,255,255)

    uncategories_products = Product.objects.filter(Q(nwd_main_category__isnull=True) |  Q(nwd_subcategory__isnull=True))
    row = 1
    for product in uncategories_products:
        
        w_sheet.write(row, 0, str(product.gtin)) # row, column, value
        w_sheet.write(row, 1, str(product.gln))

        product_names = ProductName.objects.filter(product = product, language_code = "de")
        if product_names.exists():
            w_sheet.write(row, 3, product_names[0].name)
    
        nutrition_facts = NutritionFact.objects.filter(nutrition_facts_group__nutrition__product = product)
        
        kcal = nutrition_facts.filter(canonical_name="energyKcal")
        kj = nutrition_facts.filter(canonical_name="energyKJ")
        total_fat = nutrition_facts.filter(canonical_name="totalFat")
        saturated_fat = nutrition_facts.filter(canonical_name="saturatedFat")
        carbonate = nutrition_facts.filter(canonical_name="totalCarbohydrate")
        sugar = nutrition_facts.filter(canonical_name="sugars")
        fibers = nutrition_facts.filter(canonical_name="dietaryFiber")
        protein = nutrition_facts.filter(canonical_name="protein")
        salt = nutrition_facts.filter(canonical_name="salt")
        natrium = nutrition_facts.filter(canonical_name="sodium")
        __add_value(w_sheet, row, 7, kcal, "kcal_color", False)
        __add_value(w_sheet, row, 8, kj, "kcal_color", False)
        __add_value(w_sheet, row, 9, total_fat, "fat_color", False)
        __add_value(w_sheet, row, 10, saturated_fat, "fat_color", False)
        __add_value(w_sheet, row, 11, carbonate, "carbonate_color", False)
        __add_value(w_sheet, row, 12, sugar, "carbonate_color", False)
        __add_value(w_sheet, row, 13, fibers, "carbonate_color", False)
        __add_value(w_sheet, row, 14, protein, "protein_color", False)
        __add_value(w_sheet, row, 15, salt, "salt_color", True)
        __add_value(w_sheet, row, 17, natrium, "salt_color", True)

        nutrition_attributes = NutritionAttribute.objects.filter(nutrition__product = product, language_code = "de", canonical_name="ingredients")
        if nutrition_attributes.exists():
            if hasattr(nutrition_attributes[0], "value"):
                w_sheet.write(row, 20, nutrition_attributes[0].value)

        product_attributes = ProductAttribute.objects.filter(product = product, canonical_name="packageSize")
        if product_attributes.exists():
            if hasattr(product_attributes[0], "value"):
                w_sheet.write(row, 19, product_attributes[0].value)
        row = row + 1
    workbook.save(settings.BASE_DIR + "/TrustBoxAPI/static/category/" + UNCATEGORISED_FILE_NAME) 


def __add_value(w_sheet, row, column, queryset, color, takeUnit):
    if queryset.exists():
        style = xlwt.easyxf('pattern: pattern solid, fore_colour ' + color + ';')
        if hasattr(queryset[0], "amount"):
            if is_number(str(queryset[0].amount)):
                value = float(queryset[0].amount)
            else:
                value = str(queryset[0].amount)
        elif hasattr(queryset[0], "combined_amount_and_measure"):
            if is_number(str(queryset[0].combined_amount_and_measure)): 
                value = float(queryset[0].combined_amount_and_measure)
            else:
                value = str(queryset[0].combined_amount_and_measure)
        else:
            value = ""
            w_sheet.write(row, column, value, style)
        if takeUnit:
                if hasattr(queryset[0], "unit_of_measure"):
                    if str(queryset[0].unit_of_measure) == None:
                        unit = ""
                    else:
                        unit = str(queryset[0].unit_of_measure)
                    w_sheet.write(row, column+1, unit, style)

def isint(x):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


