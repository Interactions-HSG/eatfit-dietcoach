import pytest

from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import status

from model_mommy import mommy
from models import Matching, NonFoundMatching, Product, ErrorLog, DigitalReceipt, ReceiptToNutritionUser, \
    ReceiptToNutritionPartner, MajorCategory, MinorCategory

from django.contrib.auth.models import User

from views.views import __calculate_nutri_score
import datetime

# dt = datetime.datetime.now()
#
# @pytest.mark.django_db
# def test_send_receipts_match():
#     username = 'test'
#     password = 'test'
#
#     django_user = mommy.make(User, username=username)
#     django_user.set_password(password)
#     django_user.save()
#
#     partner = ReceiptToNutritionPartner.objects.create(user=django_user, name='test')
#     user = ReceiptToNutritionUser.objects.create(r2n_partner=partner, r2n_username=username, r2n_user_active=True)
#     # major_category = MajorCategory.objects.create(pk=9, name_de="Fruchte")
#     # minor_category = MinorCategory.objects.create(pk=40, name_de="Fruchte frisch")
#     # product_item = mommy.make(Product, gtin=7613269583707, major_category=major_category, minor_category=minor_category,
#     #                           data_score=42, ofcom_value=-1, )
#     # receipt = mommy.make(DigitalReceipt, r2n_user=user, article_id='MBud Cherrytomaten', article_type='Migros_long_v1')
#     # matching = Matching.objects.create(article_id='MBud Cherrytomaten', article_type='Migros_long_v1',
#     #                                    gtin=7613269583707)
#
#     url = reverse('send-receipts-experimental')
#     client = APIClient()
#
#     payload = {
#         "r2n_partner": "test",
#         "r2n_username": "test",
#         "receipts": [
#             {
#                 "receipt_id": "1",
#                 "business_unit": "Migros",
#                 "receipt_datetime": dt,
#                 "items": [
#                     {
#                         "article_id": "MBud Cherrytomaten",
#                         "article_type": "Migros_long_v1",
#                         "quantity": 1,
#                         "quantity_unit": "units",
#                         "price": 0.9,
#                         "price_currency": "CHF"
#                     }
#                 ]}
#         ]
#     }
#
#     import base64
#     client.login(username=username, password=password)
#     credentials = base64.b64encode('{username}:{password}'.format(username=username, password=password).encode('utf-8'))
#     client.credentials(HTTP_AUTHORIZATION='Basic {}'.format(credentials.decode('utf-8')))
#
#     response = client.post(url, payload, format='json')
#     response_json = response.json()
#     print(response_json)
#
#     response_target = {
#                           u"nutriscore_indexed": 1,
#                           u"r2n_version_code": 1,
#                           u"receipt_id": u"1",
#                           u"business_unit": u"Migros",
#                           u"receipt_datetime": unicode(dt),
#                           u"nutriscore": u"A"
#                       }
#
#     assert response.status_code == status.HTTP_200_OK
#     assert len(response_json['receipts']) == 1
#     assert response_json['receipts'][0] == response_target


@pytest.mark.django_db
def test_calculate_nutriscore_match():
    username = 'test'
    password = 'test'

    django_user = mommy.make(User, username=username, password=password)
    django_user.set_password(password)
    django_user.save()

    partner = ReceiptToNutritionPartner(user=django_user, name='test')
    partner.save()

    user = ReceiptToNutritionUser(r2n_partner=partner, r2n_username=username, r2n_user_active=True)
    user.save()

    receipt = mommy.make(DigitalReceipt, r2n_user=user, article_id='MBud Cherrytomaten', article_type='Migros_long_v1')
    matching = Matching.objects.create(article_id='MBud Cherrytomaten', article_type='Migros_long_v1',
                                       gtin=7613269583707)

    category = MajorCategory.objects.create(pk=9, name_de="Fruchte")

    product_item = mommy.make(Product, gtin=7613269583707, major_category=category)

    ofcom, nutriscore, product = __calculate_nutri_score(receipt)

    assert ofcom == 1
    assert nutriscore == 1
    assert product == product_item
