from celery.decorators import periodic_task, task
from celery.task.schedules import crontab
from datetime import datetime
import requests

from NutritionService.data_import import AllergensImport, NutrientsImport, ProductsImport
from NutritionService.helpers import store_image
from NutritionService.models import Ingredient, NutritionFact, Product, NotFoundLog, calculate_ofcom_value

NUTRIENTS = ["energyKcal", "energyKJ", "protein", "salt", "sodium", "dietaryFiber", "saturatedFat", "sugars",
             "totalCarbohydrate", "totalFat"]
NUTRIENTS_MAPPING_OPENFOOD = {"energyKJ": "energy", "protein": "protein", "salt": "salt", "dietaryFiber": "fiber",
                              "saturatedFat": "saturated_fat", "sugars": "sugars", "totalCarbohydrate": "carbohydrates",
                              "totalFat": "fat"}

@task(name='tasks.execute_allergen_import_task', bind=True)
def execute_allergen_import_task(self, csv_file_path, form_data):
    importer = AllergensImport(csv_file_path, form_data)
    importer.execute_import(id=csv_file_path)

@task(name='tasks.execute_nutrient_import_task', bind=True)
def execute_nutrient_import_task(self, csv_file_path, form_data):
    importer = NutrientsImport(csv_file_path, form_data)
    importer.execute_import(id=csv_file_path)

@task(name='tasks.execute_product_import_task', bind=True)
def execute_product_import_task(self, csv_file_path, form_data):
    importer = ProductsImport(csv_file_path, form_data)
    importer.execute_import(id=csv_file_path)

@periodic_task(
    run_every=(crontab(hour=0, minute=10)),
    name="import_from_openfood",
    ignore_result=True
)
def import_from_openfood():
    not_found_items = NotFoundLog.objects.filter(processed=False)
    items_found = []
    for not_found_item in not_found_items:
        gtin = str(not_found_item.gtin)
        response = requests.get('https://www.openfood.ch/api/v3/products?barcodes=' + gtin,
                                headers={'Authorization': 'Token 8aba669f7dfc4fcc2ebf30d610bfa84f'})
        products = response.json()
        not_found_item.processed = True
        for p in products["data"][:1]:
            items_found.append(p["barcode"])
            product = Product()
            product.source = Product.OPENFOOD
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
                    Ingredient.objects.update_or_create(product=product, lang=key,
                                                        defaults={"text": unicode(p["ingredients_translations"][key])})

            if "nutrients" in p:
                nutrients = p["nutrients"]
                nutrition_facts_to_create = []
                if "salt" in nutrients:
                    nutrition_fact1 = NutritionFact(product=product, name="salt",
                                                    amount=nutrients["salt"]["per_hundred"],
                                                    unit_of_measure=nutrients["salt"]["unit"])
                    nutrition_facts_to_create.append(nutrition_fact1)

                if "energy" in nutrients:
                    nutrition_fact3 = NutritionFact(product=product, name="energyKJ",
                                                    amount=nutrients["energy"]["per_hundred"],
                                                    unit_of_measure=nutrients["energy"]["unit"])
                    nutrition_facts_to_create.append(nutrition_fact3)

                if "fat" in nutrients:
                    nutrition_fact4 = NutritionFact(product=product, name="totalFat",
                                                    amount=nutrients["fat"]["per_hundred"],
                                                    unit_of_measure=nutrients["fat"]["unit"])
                    nutrition_facts_to_create.append(nutrition_fact4)

                if "saturated_fat" in nutrients:
                    nutrition_fact5 = NutritionFact(product=product, name="saturatedFat",
                                                    amount=nutrients["saturated_fat"]["per_hundred"],
                                                    unit_of_measure=nutrients["saturated_fat"]["unit"])
                    nutrition_facts_to_create.append(nutrition_fact5)

                if "carbohydrates" in nutrients:
                    nutrition_fact6 = NutritionFact(product=product, name="totalCarbohydrate",
                                                    amount=nutrients["carbohydrates"]["per_hundred"],
                                                    unit_of_measure=nutrients["carbohydrates"]["unit"])
                    nutrition_facts_to_create.append(nutrition_fact6)

                if "sugars" in nutrients:
                    nutrition_fact7 = NutritionFact(product=product, name="sugars",
                                                    amount=nutrients["sugars"]["per_hundred"],
                                                    unit_of_measure=nutrients["sugars"]["unit"])
                    nutrition_facts_to_create.append(nutrition_fact7)

                if "fiber" in nutrients:
                    nutrition_fact8 = NutritionFact(product=product, name="dietaryFiber",
                                                    amount=nutrients["fiber"]["per_hundred"],
                                                    unit_of_measure=nutrients["fiber"]["unit"])
                    nutrition_facts_to_create.append(nutrition_fact8)

                if "protein" in nutrients:
                    nutrition_fact9 = NutritionFact(product=product, name="protein",
                                                    amount=nutrients["protein"]["per_hundred"],
                                                    unit_of_measure=nutrients["protein"]["unit"])
                    nutrition_facts_to_create.append(nutrition_fact9)

                NutritionFact.objects.bulk_create(nutrition_facts_to_create)
                calculate_ofcom_value(product)
    if len(items_found) > 0:
        NotFoundLog.objects.filter(gtin__in=items_found).delete()


def update_from_openfood(product, fields_to_update):
    response = requests.get('https://www.openfood.ch/api/v3/products?barcodes=' + str(product.gtin),
                            headers={'Authorization': 'Token 8aba669f7dfc4fcc2ebf30d610bfa84f'})
    products = response.json()
    for p in products["data"][:1]:
        if "product_size" in fields_to_update and not product.product_size:
            product.product_size = str(p["quantity"])
        if "product_size_unit_of_measure" in fields_to_update and not product.product_size_unit_of_measure:
            product.product_size_unit_of_measure = p["unit"]
        if "portion_quantity" in p and "serving_size" in fields_to_update and not product.serving_size:
            product.serving_size = str(p["portion_quantity"])

        if "name_translations" in p:
            if "product_name_de" in fields_to_update and "de" in p["name_translations"]:
                product.product_name_de = unicode(p["name_translations"]["de"])
            if "product_name_fr" in fields_to_update and "fr" in p["name_translations"]:
                product.product_name_fr = unicode(p["name_translations"]["fr"])
            if "product_name_it" in fields_to_update and "it" in p["name_translations"]:
                product.product_name_it = unicode(p["name_translations"]["it"])
            if "product_name_en" in fields_to_update and "en" in p["name_translations"]:
                product.product_name_en = unicode(p["name_translations"]["en"])

        if "image" in fields_to_update:
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

            if "nutrients" in fields_to_update and "nutrients" in p:
                try:
                    nutrients_openfood = p["nutrients"]
                    nutrition_facts_to_create = []
                    existing_nutrients = set(NutritionFact.objects.filter(product=product).values_list("name"))
                    for n in NUTRIENTS:
                        if n not in existing_nutrients and n in NUTRIENTS_MAPPING_OPENFOOD and \
                                NUTRIENTS_MAPPING_OPENFOOD[n] in nutrients_openfood:
                            nutrient_to_create = NutritionFact(product=product, name=n,
                                                               amount=nutrients_openfood[NUTRIENTS_MAPPING_OPENFOOD[n]][
                                                                   "per_hundred"], unit_of_measure=
                                                               nutrients_openfood[NUTRIENTS_MAPPING_OPENFOOD[n]][
                                                                   "unit"])
                            nutrition_facts_to_create.append(nutrient_to_create)
                    if len(nutrition_facts_to_create) > 0:
                        NutritionFact.objects.bulk_create(nutrition_facts_to_create)
                except Exception as e:
                    print(e)
    product.quality_checked = datetime.now()
    product.save()


def import_from_open_world_food_facts():
    not_found_items = NotFoundLog.objects.filter(processed=False)
    items_found = []
    for not_found_item in not_found_items:
        gtin = str(not_found_item.gtin)
        response = requests.get("https://world.openfoodfacts.org/api/v0/product/" + gtin + ".json")
        product = response.json()
        not_found_item.processed = True
        if "product" in product:
            p = product["product"]
            items_found.append(p["code"])
            product = Product()
            product.source = Product.OPENFOOD
            product.gtin = p["code"]
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
                    Ingredient.objects.update_or_create(product=product, lang=key,
                                                        defaults={"text": unicode(p["ingredients_translations"][key])})

            if "nutrients" in p:
                nutrients = p["nutrients"]
                nutrition_facts_to_create = []
                if "salt" in nutrients:
                    nutrition_fact1 = NutritionFact(product=product, name="salt",
                                                    amount=nutrients["salt"]["per_hundred"],
                                                    unit_of_measure=nutrients["salt"]["unit"])
                    nutrition_facts_to_create.append(nutrition_fact1)

                if "energy" in nutrients:
                    nutrition_fact3 = NutritionFact(product=product, name="energyKJ",
                                                    amount=nutrients["energy"]["per_hundred"],
                                                    unit_of_measure=nutrients["energy"]["unit"])
                    nutrition_facts_to_create.append(nutrition_fact3)

                if "fat" in nutrients:
                    nutrition_fact4 = NutritionFact(product=product, name="totalFat",
                                                    amount=nutrients["fat"]["per_hundred"],
                                                    unit_of_measure=nutrients["fat"]["unit"])
                    nutrition_facts_to_create.append(nutrition_fact4)

                if "saturated_fat" in nutrients:
                    nutrition_fact5 = NutritionFact(product=product, name="saturatedFat",
                                                    amount=nutrients["saturated_fat"]["per_hundred"],
                                                    unit_of_measure=nutrients["saturated_fat"]["unit"])
                    nutrition_facts_to_create.append(nutrition_fact5)

                if "carbohydrates" in nutrients:
                    nutrition_fact6 = NutritionFact(product=product, name="totalCarbohydrate",
                                                    amount=nutrients["carbohydrates"]["per_hundred"],
                                                    unit_of_measure=nutrients["carbohydrates"]["unit"])
                    nutrition_facts_to_create.append(nutrition_fact6)

                if "sugars" in nutrients:
                    nutrition_fact7 = NutritionFact(product=product, name="sugars",
                                                    amount=nutrients["sugars"]["per_hundred"],
                                                    unit_of_measure=nutrients["sugars"]["unit"])
                    nutrition_facts_to_create.append(nutrition_fact7)

                if "fiber" in nutrients:
                    nutrition_fact8 = NutritionFact(product=product, name="dietaryFiber",
                                                    amount=nutrients["fiber"]["per_hundred"],
                                                    unit_of_measure=nutrients["fiber"]["unit"])
                    nutrition_facts_to_create.append(nutrition_fact8)

                if "protein" in nutrients:
                    nutrition_fact9 = NutritionFact(product=product, name="protein",
                                                    amount=nutrients["protein"]["per_hundred"],
                                                    unit_of_measure=nutrients["protein"]["unit"])
                    nutrition_facts_to_create.append(nutrition_fact9)

                NutritionFact.objects.bulk_create(nutrition_facts_to_create)
                calculate_ofcom_value(product)
    if len(items_found) > 0:
        NotFoundLog.objects.filter(gtin__in=items_found).delete()
