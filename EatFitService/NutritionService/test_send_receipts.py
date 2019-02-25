from __future__ import print_function
import pytest
from model_mommy import mommy
from .views import views
from models import Matching, NonFoundMatching, ErrorLog, DigitalReceipt, ReceiptToNutritionUser, \
    ReceiptToNutritionPartner, MajorCategory, MinorCategory, Product, User


@pytest.mark.django_db
def test_category_logging():

    r2n_partner = mommy.make(ReceiptToNutritionPartner)
    r2n_user = mommy.make(ReceiptToNutritionUser,
                          r2n_partner=r2n_partner)

    major_category = mommy.make(MajorCategory)
    minor_category = mommy.make(MinorCategory, category_major=major_category)

    product = mommy.make(Product,
                         major_category=major_category,
                         minor_category=minor_category)

    # Foreign Keys:
    # major_category
    # minor_category

    digital_receipt = mommy.make(DigitalReceipt,
                                 r2n_user=r2n_user,
                                 business_unit='Migros')
    # match = mommy.make(Matching,
    #                    article_id=getattr(digital_receipt, 'article_id'),
    #                    article_type=getattr(digital_receipt, 'article_type'),
    #                    gtin=getattr(product, 'gtin'),
    #                    eatfit_product=product)

    mommy.make(NonFoundMatching, article_id=digital_receipt.article_id, article_type="Mafia")

    views.match_receipt(digital_receipt)

    assert NonFoundMatching.objects.all().count() == 2
