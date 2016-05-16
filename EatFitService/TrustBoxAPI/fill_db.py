from suds.client import Client
import json
from EatFitService import settings
from TrustBoxAPI.models import Product, ProductName, ProductAttribute, Nutrition, NutritionAttribute, NutritionFactsGroup, NutritionFact, AgreedData, ImportLog
from datetime import datetime

def fill():
    try:
        client = Client(settings.TRUSTBOX_URL)
        result = client.service.getChangedArticles('2016-04-18T07:30:47Z', settings.TRUSTBOX_USERNAME, settings.TRUSTBOX_PASSWORD)
        gtin_list = ""
        first = True
        i = 0
        for article in result.article:
            if first:
                first = False
                gtin_list = gtin_list + article.gtin
            else:
                gtin_list = gtin_list + "," +  article.gtin

        products = client.service.getTrustedDataByGTIN(gtin_list, settings.TRUSTBOX_USERNAME, settings.TRUSTBOX_PASSWORD)
    
        for product_list in products.productList:
            for product in product_list:
                for p in product[1]:
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
        ImportLog.objects.create(import_timestamp = datetime.now(), successful=True)
    except Exception as e:
        ImportLog.objects.create(import_timestamp = datetime.now(), successful=False, failed_reason = str(e))

def create_or_update_agreed_data(product, db_product):
    for agreed_data in product.agreedData:
       db_agreed_data, created = AgreedData.objects.update_or_create(
            agreed_id=agreed_data._agreedID, value = agreed_data.value.encode('utf8'),product =  db_product,
        )

def create_or_update_product_names(product, db_product):
    for product_names in product.productNames:
        db_product_name, created = ProductName.objects.update_or_create(
            language_code=product_names._languageCode, country_code = product_names._countryCode,product =  db_product,
            defaults={'name': product_names.name.encode('utf8')},
        )


def create_or_update_product_attributes(product, db_product):
    for product_attribute in product.productAttributes:
        if hasattr(product_attribute, '_languageCode'):
            db_product_attribute, created = ProductAttribute.objects.update_or_create(
                canonical_name=product_attribute._canonicalName, country_code = product_attribute._countryCode, language_code = product_attribute._languageCode,product =  db_product,
                defaults={'value': product_attribute.value.encode('utf8')},
            )
        else:
            db_product_attribute, created = ProductAttribute.objects.update_or_create(
                canonical_name=product_attribute._canonicalName, country_code = product_attribute._countryCode,product =  db_product,
                defaults={'value': product_attribute.value.encode('utf8')},
            )

def create_or_update_nutrition(product, db_product):
    db_nutrition, created = Nutrition.objects.get_or_create(
        product=db_product,
    )
    create_or_update_nutrition_attributes(product.nutrition, db_nutrition)
    create_or_update_nutrition_facts_group(product.nutrition, db_nutrition)

def create_or_update_nutrition_attributes(nutrition, db_nutrition):
    for nutrition_atts in nutrition.nutritionAttributes:
        if hasattr(nutrition_atts, '_languageCode'):
            db_nutrition_att, created = NutritionAttribute.objects.update_or_create(
                    canonical_name=nutrition_atts._canonicalName, country_code = nutrition_atts._countryCode,language_code = nutrition_atts._languageCode, nutrition = db_nutrition,
                    defaults={'value': nutrition_atts.value.encode('utf8')},
                )
        else:
            db_nutrition_att, created = NutritionAttribute.objects.update_or_create(
                    canonical_name=nutrition_atts._canonicalName, country_code = nutrition_atts._countryCode,nutrition = db_nutrition,
                    defaults={'value': nutrition_atts.value.encode('utf8')},
                )

def create_or_update_nutrition_facts_group(nutrition, db_nutrition):
    db_nutrition_facts_group, created = NutritionFactsGroup.objects.get_or_create(
        nutrition=db_nutrition,
    )
    create_or_update_nutrition_fact(nutrition.nutritionFactsGroups, db_nutrition_facts_group)

def create_or_update_nutrition_fact(nutrition_facts_group, db_nutrition_facts_group):
    for nutrition_fact in nutrition_facts_group.nutritionFacts:
        if hasattr(nutrition_fact, 'amount') and hasattr(nutrition_fact, 'unit_of_measure'):
            db_nutrition_fact, created = NutritionFact.objects.update_or_create(
                    canonical_name=nutrition_fact._canonicalName, country_code = nutrition_fact._countryCode, nutrition_facts_group = db_nutrition_facts_group,
                    defaults={'amount': nutrition_fact.amount,'unit_of_measure': nutrition_fact.unitOfMeasure.encode('utf8')},
                )