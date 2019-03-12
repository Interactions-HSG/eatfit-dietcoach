from django.core import files
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
import requests
import tempfile
import random
import string
import csv
import cv2
from skimage.measure import compare_ssim

from EatFitService.NutritionService.models import AdditionalImage


def calculate_image_ssim(image_original, image_new):
    original = cv2.imread(image_original)
    new = cv2.imread(image_new)

    original = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    new = cv2.cvtColor(new, cv2.COLOR_BGR2GRAY)

    ssim = compare_ssim(original, new)

    return ssim


def store_image_optim(url, product):
    img = requests.get(url, stream=True)
    if img.ok:
        file_name = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20)) + '.jpg'
        temp = tempfile.NamedTemporaryFile()

        for chunk in img.iter_content(1024):
            temp.write(chunk)

        if product.image:

            ssim = calculate_image_ssim(product.image, temp)

            if ssim <= 0.75:  # Structural similarity: 1 = perfect similarity, -1 = perfect dissimilarity
                product.image.save(file_name, files.File(temp))
            else:
                return AdditionalImage(product=product, image=files.File(temp), image_url=url)
        else:
            product.image.save(file_name, files.File(temp))


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
    except:
        return False, None


def download_csv(request, queryset):
    if not request.user.is_staff:
        raise PermissionDenied
    opts = queryset.model._meta
    response = HttpResponse(content_type='text/csv')
    # force download.
    response['Content-Disposition'] = 'attachment;filename=export.csv'
    # the csv writer
    writer = csv.writer(response)
    field_names = [field.name for field in opts.fields]
    # Write a first row with header information
    writer.writerow(field_names)
    # Write data rows
    for obj in queryset:
        writer.writerow([unicode(getattr(obj, field)).encode('utf-8') for field in field_names])
    return response
