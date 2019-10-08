from __future__ import print_function
import pytest
from model_mommy import mommy

from django.conf import settings
from django.contrib.auth.models import User

from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from rest_framework import status

from NutritionService.views import views
from NutritionService.models import NonFoundMatching, DigitalReceipt, ReceiptToNutritionUser, \
    ReceiptToNutritionPartner, MajorCategory, MinorCategory, Product, Matching
from request_data import generate_request_long


@pytest.mark.django_db
def test_category_logging():
    r2n_partner = mommy.make(ReceiptToNutritionPartner)
    r2n_user = mommy.make(ReceiptToNutritionUser,
                          r2n_partner=r2n_partner)

    major_category = mommy.make(MajorCategory)
    minor_category = mommy.make(MinorCategory, category_major=major_category)

    mommy.make(Product,
               major_category=major_category,
               minor_category=minor_category)

    digital_receipt = mommy.make(DigitalReceipt,
                                 r2n_user=r2n_user,
                                 business_unit='Migros')

    mommy.make(NonFoundMatching, article_id=digital_receipt.article_id, article_type=digital_receipt.article_type)

    views.match_receipt(digital_receipt)

    test_case = NonFoundMatching.objects.get(article_id=digital_receipt.article_id,
                                             article_type=digital_receipt.article_type)

    assert test_case.counter == 1


@pytest.mark.django_db
def test_matching_duplicate():
    r2n_partner = mommy.make(ReceiptToNutritionPartner)
    r2n_user = mommy.make(ReceiptToNutritionUser,
                          r2n_partner=r2n_partner)

    major_category = mommy.make(MajorCategory)
    minor_category = mommy.make(MinorCategory, category_major=major_category)

    product = mommy.make(Product,
                         major_category=major_category,
                         minor_category=minor_category)

    digital_receipt = mommy.make(DigitalReceipt,
                                 r2n_user=r2n_user,
                                 business_unit='Migros')

    # Test product is attached to matching
    matching1 = mommy.make(Matching, article_id=digital_receipt.article_id, article_type=digital_receipt.article_type,
                           eatfit_product=product)
    assert matching1.eatfit_product == product
    assert Matching.objects.all().count() == 1

    # Baseline test with one matching object
    matched_product = views.match_receipt(digital_receipt)
    assert matched_product == matching1.eatfit_product

    # Test duplicate matching
    matching2 = mommy.make(Matching, article_id=digital_receipt.article_id, article_type=digital_receipt.article_type,
                           eatfit_product=product)
    assert Matching.objects.all().count() == 2
    matched_product = views.match_receipt(digital_receipt)

    # Matching should return one of the matchings, no order specified yet
    assert matched_product in [matching1.eatfit_product, matching2.eatfit_product]


@pytest.mark.django_db
def test_digital_receipt_creation():
    settings.USE_TZ = True

    r2n_partner = mommy.make(ReceiptToNutritionPartner)
    r2n_user = mommy.make(ReceiptToNutritionUser,
                          r2n_partner=r2n_partner)

    data = generate_request_long(r2n_partner, r2n_user)

    digital_receipt_list = []
    response_object_ok = []
    response_object_error = []

    for receipt in data['receipts'][10:]:
        for article in receipt["items"]:
            digital_receipt = DigitalReceipt(r2n_user=r2n_user,
                                             business_unit=receipt["business_unit"],
                                             receipt_id=receipt["receipt_id"],
                                             receipt_datetime=receipt["receipt_datetime"],
                                             article_id=article["article_id"],
                                             article_type=article["article_type"],
                                             quantity=article["quantity"],
                                             quantity_unit=article["quantity_unit"],
                                             price=article["price"],
                                             price_currency=article["price_currency"])

            digital_receipt_list.append(digital_receipt)

            receipt_object = {
                "receipt_id": receipt["receipt_id"],
                "receipt_datetime": receipt["receipt_datetime"],
                "business_unit": receipt["business_unit"],
                "nutriscore": "PASS",
                "nutriscore_indexed": "PASS",
                "r2n_version_code": 1
            }

            response_object_ok.append(receipt_object)

    for receipt in data['receipts'][:10]:
        for article in receipt["items"]:
            digital_receipt = DigitalReceipt(r2n_user=r2n_user,
                                             business_unit=receipt["business_unit"],
                                             receipt_id=receipt["receipt_id"],
                                             receipt_datetime=receipt["receipt_datetime"],
                                             article_id=article["article_id"],
                                             article_type=article["article_type"],
                                             quantity=article["quantity"],
                                             quantity_unit=article["quantity_unit"],
                                             price=article["price"],
                                             price_currency=article["price_currency"])

            digital_receipt_list.append(digital_receipt)

            receipt_object = {
                "receipt_id": receipt["receipt_id"],
                "receipt_datetime": receipt["receipt_datetime"],
                "business_unit": receipt["business_unit"],
                "nutriscore": "error: maximum amount of calls exceeded",
                "nutriscore_indexed": "error: maximum amount of calls exceeded",
                "r2n_version_code": 1
            }

            response_object_error.append(receipt_object)

    DigitalReceipt.objects.bulk_create(digital_receipt_list)

    assert len(response_object_ok) <= 10
    assert len(DigitalReceipt.objects.all()) == len(digital_receipt_list)
    assert len(digital_receipt_list) == len(response_object_ok) + len(response_object_error)


@pytest.mark.django_db
def test_product_size_of_measurement():
    user = User.objects.create_user(username='test', password='test')

    api_client = APIClient()
    api_client.force_authenticate(user=user)

    url = reverse('send-receipts-experimental')

    r2n_partner = mommy.make(ReceiptToNutritionPartner, user=user)
    r2n_user = mommy.make(ReceiptToNutritionUser,
                          r2n_partner=r2n_partner)
    major_category = mommy.make(MajorCategory)
    minor_category = mommy.make(MinorCategory, category_major=major_category)

    # Catch TypeError

    product = mommy.make(Product,
                         major_category=major_category,
                         minor_category=minor_category,
                         product_size=None,
                         product_size_unit_of_measure=None)

    mommy.make(Matching, article_id='Apfel Braeburn', article_type='Migros_long_v1', eatfit_product=product)

    data = {
        "r2n_partner": r2n_partner.name,
        "r2n_username": r2n_user.r2n_username,
        "receipts": [
            {
                "receipt_id": "1551533421",
                "receipt_datetime": "2019-03-02T14:30:21Z",
                "business_unit": "Migros",
                "items": [
                    {
                        "article_id": "Apfel Braeburn",
                        "article_type": "Migros_long_v1",
                        "quantity": 0.712,
                        "quantity_unit": "kg",
                        "price": "1.85",
                        "price_currency": "CHF"
                    }
                ]
            }
        ]
    }

    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK

    # Catch ValueError

    product = mommy.make(Product,
                         major_category=major_category,
                         minor_category=minor_category,
                         product_size='Huge',
                         product_size_unit_of_measure='ugdugilawg')

    mommy.make(Matching, article_id='Apfel Braeburn', article_type='Migros_long_v1', eatfit_product=product)

    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
