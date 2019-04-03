import pytest

from django.core.files.uploadedfile import SimpleUploadedFile

from NutritionService.helpers import calculate_image_ssim


def test_calculate_ssim_same_image():

    with open('NutritionService/tests/product_image.jpg') as infile:
        first_image = SimpleUploadedFile(infile.name, infile.read())

    with open('NutritionService/tests/product_image.jpg') as infile:
        second_image = SimpleUploadedFile(infile.name, infile.read())

    ssim = calculate_image_ssim(first_image, second_image, original_buffered=True, new_buffered=True)

    assert ssim == 1


def test_calculate_ssim_same_array_shape():

    with open('NutritionService/tests/product_image.jpg') as infile:
        first_image = SimpleUploadedFile(infile.name, infile.read())

    with open('NutritionService/tests/other_image.jpg') as infile:
        second_image = SimpleUploadedFile(infile.name, infile.read())

    ssim = calculate_image_ssim(first_image, second_image, original_buffered=True, new_buffered=True)

    assert ssim < 1


def test_calculate_ssim_different_array_shape():

    with open('NutritionService/tests/product_image.jpg') as infile:
        first_image = SimpleUploadedFile(infile.name, infile.read())

    with open('NutritionService/tests/bad_image.jpg') as infile:
        second_image = SimpleUploadedFile(infile.name, infile.read())

    ssim = calculate_image_ssim(first_image, second_image, original_buffered=True, new_buffered=True)

    assert ssim is None
