import requests
from NutritionService.helpers import store_image
from NutritionService.models import Ingredient
from NutritionService.models import NutritionFact
from NutritionService.models import Product
from NutritionService.models import NotFoundLog
from celery.decorators import periodic_task
from celery.task.schedules import crontab


@periodic_task(
    run_every=(crontab(hour=0, minute=10)),
    name="import_from_openfood",
    ignore_result=True
)
def import_from_openfood():
    not_found_items = NotFoundLog.objects.all()

    for not_found_item in not_found_items:
        gtin = str(not_found_item.gtin)
        response = requests.get('https://www.openfood.ch/api/v3/products?barcodes=' + gtin, headers={'Authorization': 'Token 8aba669f7dfc4fcc2ebf30d610bfa84f'})
        products = response.json()

        for p in products["data"]:
            product = Product()
            product.gtin = p["barcode"]
            product.product_size = str(p["quantity"])
            product.product_size_unit_of_measure = p["unit"]
            if "portion_quantity" in p:
                product.serving_size = str(p["portion_quantity"])

            if "name_translations" in p:
                if "de" in p["name_translations"]:
                    product.product_name_de = unicode(p["name_translations"]["de"])
                if "fr" in p["name_translations"]:
                    product.product_name_fr = unicode(p["name_translations"]["fr"])
                if "it" in p["name_translations"]:
                    product.product_name_it = unicode(p["name_translations"]["it"])
                if "en" in p["name_translations"]:
                    product.product_name_en = unicode(p["name_translations"]["en"])

            product.save()

            image_url = None
            front_image_found = False
            for image in p["images"]:
                if front_image_found:
                    break
                image_url = image["large"]
                for cat in image["categories"]:
                    if cat == "Front":
                        front_image_found = True
            if image_url:
                store_image(image_url, product)

            if "ingredients_translations" in p:
                for key in p["ingredients_translations"]:
                    Ingredient.objects.update_or_create(product = product, lang = key, defaults = {"text" : unicode(p["ingredients_translations"][key])})
        
            if "nutrients" in p:
                nutrients = p["nutrients"]
                nutrition_facts_to_create = []
                if "salt" in nutrients:
                    nutrition_fact1 = NutritionFact(product = product, name = "salt", amount = nutrients["salt"]["per_hundred"], unit_of_measure = nutrients["salt"]["unit"])
                    nutrition_facts_to_create.append(nutrition_fact1)
                
                if "energy" in nutrients:
                    nutrition_fact3 = NutritionFact(product = product, name = "energyKJ", amount = nutrients["energy"]["per_hundred"], unit_of_measure = nutrients["energy"]["unit"])
                    nutrition_facts_to_create.append(nutrition_fact3)

                if "fat" in nutrients:
                    nutrition_fact4 = NutritionFact(product = product, name = "totalFat", amount = nutrients["fat"]["per_hundred"], unit_of_measure = nutrients["fat"]["unit"])
                    nutrition_facts_to_create.append(nutrition_fact4)

                if "saturated_fat" in nutrients:
                    nutrition_fact5 = NutritionFact(product = product, name = "saturatedFat", amount = nutrients["saturated_fat"]["per_hundred"], unit_of_measure = nutrients["saturated_fat"]["unit"])
                    nutrition_facts_to_create.append(nutrition_fact5)

                if "carbohydrates" in nutrients:
                    nutrition_fact6 = NutritionFact(product = product, name = "totalCarbohydrate", amount = nutrients["carbohydrates"]["per_hundred"], unit_of_measure = nutrients["carbohydrates"]["unit"])
                    nutrition_facts_to_create.append(nutrition_fact6)

                if "sugars" in nutrients:
                    nutrition_fact7 = NutritionFact(product = product, name = "sugars", amount = nutrients["sugars"]["per_hundred"], unit_of_measure = nutrients["sugars"]["unit"])
                    nutrition_facts_to_create.append(nutrition_fact7)

                if "fiber" in nutrients:
                    nutrition_fact8 = NutritionFact(product = product, name = "dietaryFiber", amount = nutrients["fiber"]["per_hundred"], unit_of_measure = nutrients["fiber"]["unit"])
                    nutrition_facts_to_create.append(nutrition_fact8)

                if "protein" in nutrients:
                    nutrition_fact9 = NutritionFact(product = product, name = "protein", amount = nutrients["protein"]["per_hundred"], unit_of_measure = nutrients["protein"]["unit"])
                    nutrition_facts_to_create.append(nutrition_fact9)

                NutritionFact.objects.bulk_create(nutrition_facts_to_create)
    not_found_items.delete()