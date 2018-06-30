import requests
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


def is_number(s):
    try:
        v = float(s)
        return True, v 
    except ValueError:
        return False, None
