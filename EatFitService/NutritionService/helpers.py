import requests
from NutritionService.models import NutritionFact
import tempfile
from django.core import files
import random
import string


ENERGY_KJ = "energyKJ"
ENERGY_KCAL = "energyKcal"
TOTAL_FAT = "totalFat"
SATURATED_FAT = "saturatedFat"
TOTAL_CARBOHYDRATE = "totalCarbohydrate"
SUGARS = "sugars"
DIETARY_FIBER = "dietaryFiber"
PROTEIN = "protein"
SALT = "salt"
SODIUM = "sodium"


def store_image(image_url, product):
    if product.original_image_url == None or product.original_image_url != image_url:
        try:
            request = requests.get(image_url, stream=True)
            # Was the request OK?
            if request.status_code != requests.codes.ok:
                return

            # Get the filename from the url, used for saving later
            file_name = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20)) + ".jpg"

            # Create a temporary file
            lf = tempfile.NamedTemporaryFile()

            # Read the streamed image in sections
            for block in request.iter_content(1024 * 8):

                # If no more file then stop
                if not block:
                    break

                # Write image block to temporary file
                lf.write(block)

            # Save the temporary image to the model#
            # This saves the model so be sure that is it valid
            product.image.save(file_name, files.File(lf))
            product.original_image_url = image_url
            product.save()
        except Exception as ex:
            print(ex)

def calculate_ofcom_value(product):
    nutrition_facts = NutritionFact.objects.filter(product = product)
    data_quality_sufficient = True
    ofcom_value = 0
    for fact in nutrition_facts:
        if not is_number(fact.amount):
            data_quality_sufficient = False
            break
        amount = float(fact.amount)
        if fact.name == ENERGY_KJ:
            ofcom_value = ofcom_value + __calcluate_ofcom_point(amount, [3350, 3015, 2680, 2345, 2010, 1675, 1340, 1005, 670, 335])
        elif fact.name == SATURATED_FAT:
            ofcom_value = ofcom_value + __calcluate_ofcom_point(amount, [10, 9, 8, 7, 6, 5, 4, 3, 2, 1])
        elif fact.name == SUGARS:
            ofcom_value = ofcom_value + __calcluate_ofcom_point(amount, [45, 40, 36, 31, 27, 22.5, 18, 13.5, 9, 4.5])
        elif fact.name == SODIUM:
            if fact.unit_of_measure == "mg":
                ofcom_value = ofcom_value + __calcluate_ofcom_point(amount, [900, 810, 720, 630, 540, 450, 360, 270, 180, 90])
            elif fact.unit_of_measure == "g":
                ofcom_value = ofcom_value + __calcluate_ofcom_point(amount, [0.9, 0.81, 0.72, 0.63, 0.54, 0.45, 0.36, 0.27, 0.18, 0.09])
            else:
                data_quality_sufficient = False
                break
        elif fact.name == DIETARY_FIBER:
            ofcom_value = ofcom_value - __calcluate_ofcom_point(amount, [3.5, 2.8, 2.1, 1.4, 0.7])
        elif fact.name == PROTEIN:
            ofcom_value = ofcom_value - __calcluate_ofcom_point(amount, [8, 6.4, 4.8, 3.2, 1.6])
    if data_quality_sufficient:
        product.ofcom_value = ofcom_value
        product.save()


def __calcluate_ofcom_point(amount, values):
    points = len(values)
    for value in values:
        if amount > value:
            return points
        points = points - 1
    return 0

def is_number(s):
    try:
        v = float(s)
        return True, v 
    except ValueError:
        return False, None
