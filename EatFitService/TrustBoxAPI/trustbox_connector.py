from suds.client import Client
import json
from EatFitService import settings
from TrustBoxAPI.models import Product, ProductName, ProductAttribute, Nutrition, NutritionAttribute, NutritionFactsGroup, NutritionFact, AgreedData, ImportLog, NutritionLabel, NutritionGroupAttribute
from datetime import datetime

DEFAULT_START_TIME = "2000-01-01T00:00:00Z"

def load_changed_data():
    try:
        log = ImportLog.objects.filter(successful=True)
        if log.exists():
            latest_log = log.latest("import_timestamp")
            start_time = latest_log.import_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            start_time = DEFAULT_START_TIME
        client = Client(settings.TRUSTBOX_URL)
        result = client.service.getChangedArticles(start_time, settings.TRUSTBOX_USERNAME, settings.TRUSTBOX_PASSWORD)
        gtin_list = ""
        first = True
        i = 0
        for article in result.article:
            products = client.service.getTrustedDataByGTIN(str(article.gtin), settings.TRUSTBOX_USERNAME, settings.TRUSTBOX_PASSWORD)

            for product_list in products.productList:
                for product in product_list:
                    for p in product[1]:
                        try:
                            i = i + 1
                            print("adding product: " + str(i))
                            db_product, created = Product.objects.update_or_create(
                                gtin=p._gtin,
                                defaults={'gln': p._gln, "target_market_country_code" : p._targetMarketCountryCode, "status" : p._status},
                            )
                            create_or_update_product_names(p, db_product)
                            create_or_update_product_attributes(p, db_product)
                            create_or_update_nutrition(p, db_product)
                            create_or_update_agreed_data(p, db_product)
                        except Exception as e:
                            ImportLog.objects.create(import_timestamp = datetime.now(), successful=False, failed_reason = "Product: " + str(p._gtin) + " " + str(e))
        ImportLog.objects.create(import_timestamp = datetime.now(), successful=True)
    except Exception as e:
        ImportLog.objects.create(import_timestamp = datetime.now(), successful=False, failed_reason = "General error: " +  str(e))

def create_or_update_agreed_data(product, db_product):
    if hasattr(product, 'agreedData'):
        for agreed_data in product.agreedData:
           db_agreed_data, created = AgreedData.objects.update_or_create(
                agreed_id=agreed_data._agreedID, value = agreed_data.value.encode('utf8'),product =  db_product,
            )

def create_or_update_product_names(product, db_product):
    if hasattr(product, 'productNames'):
        for product_names in product.productNames:
            filter_arguments = {}
            filter_arguments["product"] = db_product
            filter_arguments["language_code"] = None
            filter_arguments["country_code"] = None
            if hasattr(product_names, '_languageCode'):
                filter_arguments["language_code"] = product_names._languageCode
            if hasattr(product_names, '_countryCode'):
                filter_arguments["country_code"] = product_names._countryCode
            db_product_name, created = ProductName.objects.update_or_create(defaults={'name': product_names.name.encode('utf8')},**filter_arguments)


def create_or_update_product_attributes(product, db_product):
    if hasattr(product, 'productAttributes'):
        for product_attribute in product.productAttributes:
            filter_arguments = {}
            filter_arguments["product"] = db_product
            filter_arguments["language_code"] = None
            filter_arguments["country_code"] = None
            filter_arguments["canonical_name"] = None
            if hasattr(product_attribute, '_languageCode'):
                filter_arguments["language_code"] = product_attribute._languageCode
            if hasattr(product_attribute, '_countryCode'):
                filter_arguments["country_code"] = product_attribute._countryCode
            if hasattr(product_attribute, '_canonicalName'):
                filter_arguments["canonical_name"] = product_attribute._canonicalName
            db_product_attribute, created = ProductAttribute.objects.update_or_create(defaults={'value': product_attribute.value.encode('utf8')}, **filter_arguments)

def create_or_update_nutrition(product, db_product):
    db_nutrition, created = Nutrition.objects.get_or_create(
        product=db_product,
    )
    create_or_update_nutrition_attributes(product.nutrition, db_nutrition)
    create_or_update_nutrition_facts_group(product.nutrition, db_nutrition)
    create_or_update_nutrition_lables(product.nutrition, db_nutrition)

def create_or_update_nutrition_attributes(nutrition, db_nutrition):
    if hasattr(nutrition, "nutritionAttributes"):
        for nutrition_atts in nutrition.nutritionAttributes:
            filter_arguments = {}
            filter_arguments["nutrition"] = db_nutrition
            filter_arguments["language_code"] = None
            filter_arguments["country_code"] = None
            filter_arguments["canonical_name"] = None
            if hasattr(nutrition_atts, '_languageCode'):
                filter_arguments["language_code"] = nutrition_atts._languageCode
            if hasattr(nutrition_atts, '_countryCode'):
                filter_arguments["country_code"] = nutrition_atts._countryCode
            if hasattr(nutrition_atts, '_canonicalName'):
                filter_arguments["canonical_name"] = nutrition_atts._canonicalName
            db_nutrition_att, created = NutritionAttribute.objects.update_or_create(defaults={'value': nutrition_atts.value.encode('utf8')},**filter_arguments)

def create_or_update_nutrition_facts_group(nutrition, db_nutrition):
    db_nutrition_facts_group, created = NutritionFactsGroup.objects.get_or_create(
        nutrition=db_nutrition,
    )
    create_or_update_nutrition_fact(nutrition.nutritionFactsGroups, db_nutrition_facts_group)
    create_or_update_nutrition_group_attrs(nutrition.nutritionFactsGroups, db_nutrition_facts_group)

def create_or_update_nutrition_fact(nutrition_facts_group, db_nutrition_facts_group):
    if hasattr(nutrition_facts_group, "nutritionFacts"):
        for nutrition_fact in nutrition_facts_group.nutritionFacts:
            filter_arguments = {}
            filter_arguments["nutrition_facts_group"] = db_nutrition_facts_group
            ilter_arguments["language_code"] = None
            filter_arguments["country_code"] = None
            filter_arguments["canonical_name"] = None
            if hasattr(nutrition_fact, '_languageCode'):
                filter_arguments["language_code"] = nutrition_fact._languageCode
            if hasattr(nutrition_fact, '_countryCode'):
                filter_arguments["country_code"] = nutrition_fact._countryCode
            if hasattr(nutrition_fact, '_canonicalName'):
                filter_arguments["canonical_name"] = nutrition_fact._canonicalName
            
            data = {}
            if hasattr(nutrition_fact, 'amount'):
                data["amount"] = nutrition_fact.amount.encode('utf8')
            if hasattr(nutrition_fact, 'unitOfMeasure'):
                data["unit_of_measure"] = nutrition_fact.unitOfMeasure.encode('utf8')
            if hasattr(nutrition_fact, 'combinedAmountAndMeasure'):
                data["combined_amount_and_measure"] = nutrition_fact.combinedAmountAndMeasure.encode('utf8')
            if hasattr(nutrition_fact, 'dailyPercent'):
                data["daily_percent"] = nutrition_fact.dailyPercent.encode('utf8')

            db_nutrition_fact, created = NutritionFact.objects.update_or_create(defaults=data,**filter_arguments)

def create_or_update_nutrition_lables(nutrition, db_nutrition):
    if hasattr(nutrition, "nutritionLabels"):
        for nutrition_label in nutrition.nutritionLabels:
            filter_arguments = {}
            filter_arguments["nutrition"] = db_nutrition
            filter_arguments["language_code"] = None
            if hasattr(nutrition_label, '_languageCode'):
                filter_arguments["label_id"] = nutrition_label._labelID
            db_nutrition_label, created = NutritionLabel.objects.update_or_create(defaults={'value': nutrition_label.value.encode('utf8')},**filter_arguments)

def create_or_update_nutrition_group_attrs(nutrition_facts_group, db_nutrition_facts_group):
    if hasattr(nutrition_facts_group, "nutritionGroupAttributes"):
        for groupAttr in nutrition_facts_group.nutritionGroupAttributes:
            filter_arguments = {}
            filter_arguments["nutrition_facts_group"] = db_nutrition_facts_group
            filter_arguments["language_code"] = None
            filter_arguments["country_code"] = None
            filter_arguments["canonical_name"] = None
            if hasattr(groupAttr, '_languageCode'):
                filter_arguments["language_code"] = groupAttr._languageCode
            if hasattr(groupAttr, '_countryCode'):
                filter_arguments["country_code"] = groupAttr._countryCode
            if hasattr(groupAttr, '_canonicalName'):
                filter_arguments["canonical_name"] = groupAttr._canonicalName
            db_nutrition_group_attr, created = NutritionGroupAttribute.objects.update_or_create(defaults={'value': groupAttr.value.encode('utf8')},**filter_arguments )


def single_product_to_db(gtin):
    client = Client(settings.TRUSTBOX_URL)
    products = client.service.getTrustedDataByGTIN(gtin, settings.TRUSTBOX_USERNAME, settings.TRUSTBOX_PASSWORD)
    for product_list in products.productList:
                for product in product_list:
                    for p in product[1]:
                        try:
                            db_product, created = Product.objects.update_or_create(
                                gtin=p._gtin,
                                defaults={'gln': p._gln, "target_market_country_code" : p._targetMarketCountryCode, "status" : p._status},
                            )
                            create_or_update_product_names(p, db_product)
                            create_or_update_product_attributes(p, db_product)
                            create_or_update_nutrition(p, db_product)
                            create_or_update_agreed_data(p, db_product)
                            print("Added product: " + str(p._gtin))
                        except Exception as e:
                            print("Product: " + str(p._gtin) + " " + str(e))

def get_single_product(gtin):
    client = Client(settings.TRUSTBOX_URL)
    products = client.service.getTrustedDataByGTIN(gtin, settings.TRUSTBOX_USERNAME, settings.TRUSTBOX_PASSWORD)
    for product_list in products.productList:
                for product in product_list:
                    for p in product[1]:
                        return p
    return None