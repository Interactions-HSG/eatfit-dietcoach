from __future__ import print_function
import pytest
from model_mommy import mommy
from .views import views
from models import NonFoundMatching, DigitalReceipt, ReceiptToNutritionUser, \
    ReceiptToNutritionPartner, MajorCategory, MinorCategory, Product


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
