import csv
import cv2
import numpy as np
from PIL import Image
import random
import requests
import shutil
from skimage.measure import compare_ssim
import string
from StringIO import StringIO
import tempfile
from textblob import TextBlob

from django.core import files
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied


def detect_language(text):
    try:
        blob = TextBlob(text.decode('utf-8'))
        lang = blob.detect_language()
        return lang
    except AttributeError:
        return None


def prepare_image_buffered(image):

    temp_buffer = StringIO()
    temp_buffer.write(image.read())
    temp_buffer.seek(0)
    image = np.array(Image.open(temp_buffer), dtype=np.uint8)

    return image


def calculate_image_ssim(original_image, new_image, original_buffered=True, new_buffered=False):
    if original_buffered:
        original_image = prepare_image_buffered(original_image)
    else:
        original_image = cv2.imread(original_image.name, cv2.IMREAD_UNCHANGED)

    if new_buffered:
        new_image = prepare_image_buffered(new_image)
    else:
        new_image = cv2.imread(new_image.name, cv2.IMREAD_UNCHANGED)

    original_image_processed = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    new_image_processed = cv2.cvtColor(new_image, cv2.COLOR_BGR2GRAY)

    if original_image_processed.shape == new_image_processed.shape:
        return compare_ssim(original_image_processed, new_image_processed)
    else:
        return -99  # SSIM not meaningful for arrays of unequal dimensions / SSIM of -99 is undefined for [1, -1]


def store_image_optim(url, product):
    img = requests.get(url, stream=True, timeout=10)
    if img.ok:
        temp = tempfile.NamedTemporaryFile(suffix='.jpg')
        img.raw.decode_content = True
        shutil.copyfileobj(img.raw, temp)

        file_name = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20)) + '.jpg'

        if product.image:

            ssim = calculate_image_ssim(product.image, temp)

            if ssim <= 0.75:  # Structural similarity: 1 = perfect similarity, -1 = perfect dissimilarity
                if product.original_image_url:
                    new_image = {'image': product.image, 'image_url': product.original_image_url}
                    product.additional_image.create(**new_image)
                product.image.save(file_name, files.File(temp))
            else:
                new_image = {'image': files.File(temp), 'image_url': url}
                product.additional_image.create(**new_image)
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
        raise PermissionDenied()
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
