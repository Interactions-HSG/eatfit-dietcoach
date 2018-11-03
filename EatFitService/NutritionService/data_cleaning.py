from django.db import connection
from NutritionService.tasks import update_from_openfood
from NutritionService.models import NutritionFact, Product
from django.db.models import Q
from datetime import datetime, timedelta


def fill_product_names_and_images():
    one_month_before = datetime.now() - timedelta(days = 30)
    products = Product.objects.filter(Q(quality_checked__isnull = True) | Q(quality_checked__lt = one_month_before), product_name_de__isnull = True, automatic_update = True).order_by("quality_checked")[:50]
    for product in products:
        update_from_openfood(product, {"product_name_de" : 1, "product_name_en" : 1, "product_name_fr" : 1, "product_name_it" : 1, "image" : 1, "product_size" : 1, "product_size_unit_of_measure" : 1, "portion_quantity" : 1, "nutrients" : 1})


def clean_salt_sodium():
    with connection.cursor() as cursor:

        # products with salt > 0 and sodium = 0 
        sql = "Select n1.product_id from nutrition_fact as n1, nutrition_fact as n2 where n1.product_id = n2.product_id and n1.name = 'sodium' and n1.amount = 0 and n2.name = 'salt' and n2.amount > 0;"
        cursor.execute(sql)
        for row in cursor.fetchall():
            product_id = row[0]
            facts = NutritionFact.objects.filter(Q(name = 'salt') | Q(name = 'sodium'), product__pk = product_id)
            if facts.count() == 2:
                sodium_value = 0
                if facts[0].name == 'salt':
                    sodium_value = facts[0].amount/2.54
                    fact_to_update = facts[1]
                    fact_to_update.amount = sodium_value
                    fact_to_update.save()
                elif facts[1].name == 'salt':
                    sodium_value = facts[1].amount/2.54
                    fact_to_update = facts[0]
                    fact_to_update.amount = sodium_value
                    fact_to_update.save()

        # products with salt = 0 and sodium > 0 
        sql = "Select n1.product_id from nutrition_fact as n1, nutrition_fact as n2 where n1.product_id = n2.product_id and n1.name = 'salt' and n1.amount = 0 and n2.name = 'sodium' and n2.amount > 0;"
        cursor.execute(sql)
        for row in cursor.fetchall():
            product_id = row[0]
            facts = NutritionFact.objects.filter(Q(name = 'salt') | Q(name = 'sodium'), product__pk = product_id)
            if facts.count() == 2:
                sodium_value = 0
                if facts[0].name == 'sodium':
                    salt_value = facts[0].amount*2.54
                    fact_to_update = facts[1]
                    fact_to_update.amount = salt_value
                    fact_to_update.save()
                elif facts[1].name == 'sodium':
                    salt_value = facts[1].amount*2.54
                    fact_to_update = facts[0]
                    fact_to_update.amount = salt_value
                    fact_to_update.save()
   

