from __future__ import print_function
import pytest
from model_mommy import mommy

from django.conf import settings

from NutritionService.views import views
from NutritionService.models import NonFoundMatching, DigitalReceipt, ReceiptToNutritionUser, \
    ReceiptToNutritionPartner, MajorCategory, MinorCategory, Product
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
