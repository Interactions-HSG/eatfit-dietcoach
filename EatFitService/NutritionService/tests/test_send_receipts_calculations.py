# coding=utf-8
import pytest
from model_mommy import mommy

from django.contrib.auth.models import User

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.reverse import reverse
from rest_framework import status

from NutritionService.views import views
from NutritionService.views.errors import SendReceiptsErrors
from NutritionService.models import FOOD, NonFoundMatching, DigitalReceipt, ReceiptToNutritionUser, \
    ReceiptToNutritionPartner, MajorCategory, MinorCategory, Product, Matching, NutritionFact
from send_receipts_data import TEST_DATA, TEST_DATA_LONG, TEST_DATA_DETAILED

RECEIPTS_KEY = 'receipts'
errors = SendReceiptsErrors()

@pytest.mark.django_db
def test_product_validation():

    assert User.objects.count() == 0
    assert ReceiptToNutritionPartner.objects.count() == 0
    assert ReceiptToNutritionUser.objects.count() == 0
    assert Product.objects.count() == 0
    assert Matching.objects.count() == 0
    assert NonFoundMatching.objects.count() == 0

    user = User.objects.create_user(username='test', password='test')
    r2n_partner = mommy.make(ReceiptToNutritionPartner, user=user, name='Kevin')
    r2n_user = mommy.make(ReceiptToNutritionUser, r2n_partner=r2n_partner, r2n_username='Kevin')
    test_product = mommy.make(Product)
    mommy.make(Matching, eatfit_product=test_product, article_id='Apfel Braeburn', article_type='Migros_long_v1')

    assert test_product.product_size is None
    assert test_product.product_size_unit_of_measure is None
    assert test_product.data_score < 25
    assert test_product.minor_category is None
    assert test_product.major_category is None
    assert test_product.nutri_score_final is None

    TEST_DATA['r2n_partner'] = r2n_partner.name
    TEST_DATA['r2n_username'] = r2n_user.r2n_username

    assert User.objects.count() == 1
    assert ReceiptToNutritionPartner.objects.count() == 1
    assert ReceiptToNutritionUser.objects.count() == 1
    assert Product.objects.count() == 1
    assert Matching.objects.count() == 1

    api_client = APIRequestFactory()
    view = views.SendReceiptsView.as_view()
    url = reverse('send-receipts')
    request = api_client.post(url, TEST_DATA, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert NonFoundMatching.objects.count() == 0
    assert DigitalReceipt.objects.count() == 1
    assert RECEIPTS_KEY in response.data
    assert len(response.data[RECEIPTS_KEY]) == 1
    assert response.data[RECEIPTS_KEY][-1]['nutriscore'] == errors.UNKNOWN
    assert response.data[RECEIPTS_KEY][-1]['nutriscore_indexed'] == errors.UNKNOWN


@pytest.mark.django_db
def test_receipt_long():

    assert User.objects.count() == 0
    assert ReceiptToNutritionPartner.objects.count() == 0
    assert ReceiptToNutritionUser.objects.count() == 0
    assert MajorCategory.objects.count() == 0
    assert MinorCategory.objects.count() == 0
    assert Product.objects.count() == 0
    assert NutritionFact.objects.count() == 0
    assert Matching.objects.count() == 0
    assert NonFoundMatching.objects.count() == 0
    assert DigitalReceipt.objects.count() == 0

    user = User.objects.create_user(username='test', password='test')
    r2n_partner = mommy.make(ReceiptToNutritionPartner, user=user, name='Kevin')
    r2n_user = mommy.make(ReceiptToNutritionUser, r2n_partner=r2n_partner, r2n_username='Kevin')

    major_category = mommy.make(MajorCategory, pk=16)
    minor_category = mommy.make(MinorCategory, pk=82, category_major=major_category, nutri_score_category=FOOD)
    test_product = mommy.make(Product, gtin=1, product_name_de='Apfel Braeburn', major_category=major_category,
                              minor_category=minor_category, health_percentage=30, product_size_unit_of_measure='kg',
                              product_size='1')
    mommy.make(Matching, eatfit_product=test_product, article_id='Apfel Braeburn', article_type='Migros_long_v1',
               gtin=1)
    mommy.make(NutritionFact, product=test_product, name='totalFat', amount=0.3, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='saturatedFat', amount=0.1, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='totalCarbohydrate', amount=12.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='sugars', amount=12.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='dietaryFiber', amount=2.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='protein', amount=0.3, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='salt', amount=0.01, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='sodium', amount=0.13, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='energyKJ', amount=232.0, unit_of_measure='KJ')
    mommy.make(NutritionFact, product=test_product, name='energyKcal', amount=55.0, unit_of_measure='Kcal')
    test_product.save()

    assert test_product.product_size is not None
    assert test_product.product_size_unit_of_measure is not None
    assert test_product.data_score >= 25
    assert test_product.minor_category is not None
    assert test_product.major_category is not None
    assert test_product.nutri_score_final is not None

    TEST_DATA_LONG['r2n_partner'] = r2n_partner.name
    TEST_DATA_LONG['r2n_username'] = r2n_user.r2n_username

    assert User.objects.count() == 1
    assert ReceiptToNutritionPartner.objects.count() == 1
    assert ReceiptToNutritionUser.objects.count() == 1
    assert MajorCategory.objects.count() == 1
    assert MinorCategory.objects.count() == 1
    assert Product.objects.count() == 1
    assert Matching.objects.count() == 1
    assert NutritionFact.objects.count() == 10

    api_client = APIRequestFactory()
    view = views.SendReceiptsView.as_view()
    url = reverse('send-receipts')
    request = api_client.post(url, TEST_DATA_LONG, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert NonFoundMatching.objects.count() == 0
    assert DigitalReceipt.objects.count() == 12
    assert RECEIPTS_KEY in response.data
    assert len(response.data[RECEIPTS_KEY]) == 12
    assert response.data[RECEIPTS_KEY][-1]['nutriscore'] == errors.MAXIMUM_REACHED
    assert response.data[RECEIPTS_KEY][-1]['nutriscore_indexed'] == errors.MAXIMUM_REACHED

    

@pytest.mark.django_db
def test_receipt_valid():
    assert User.objects.count() == 0
    assert ReceiptToNutritionPartner.objects.count() == 0
    assert ReceiptToNutritionUser.objects.count() == 0
    assert MajorCategory.objects.count() == 0
    assert MinorCategory.objects.count() == 0
    assert Product.objects.count() == 0
    assert NutritionFact.objects.count() == 0
    assert Matching.objects.count() == 0
    assert NonFoundMatching.objects.count() == 0
    assert DigitalReceipt.objects.count() == 0

    user = User.objects.create_user(username='test', password='test')
    r2n_partner = mommy.make(ReceiptToNutritionPartner, user=user, name='Kevin')
    r2n_user = mommy.make(ReceiptToNutritionUser, r2n_partner=r2n_partner, r2n_username='Kevin')

    major_category = mommy.make(MajorCategory, pk=16)
    minor_category = mommy.make(MinorCategory, pk=82, category_major=major_category, nutri_score_category=FOOD)
    first_product = mommy.make(Product, gtin=1, product_name_de='DV extra fin Chia & Quinoa 4PP 184g',
                               major_category=major_category, minor_category=minor_category, health_percentage=1,
                               product_size_unit_of_measure='kg', product_size='1.729')
    mommy.make(Matching, eatfit_product=first_product, article_id='DV extra fin Chia & Quinoa 4PP 184g',
               article_type='Migros_long_v1', gtin=1)
    mommy.make(NutritionFact, product=first_product, name='totalFat', amount=16.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=first_product, name='saturatedFat', amount=1.8, unit_of_measure='g')
    mommy.make(NutritionFact, product=first_product, name='totalCarbohydrate', amount=54.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=first_product, name='sugars', amount=1.9, unit_of_measure='g')
    mommy.make(NutritionFact, product=first_product, name='dietaryFiber', amount=10.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=first_product, name='protein', amount=14.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=first_product, name='salt', amount=1.9, unit_of_measure='g')
    mommy.make(NutritionFact, product=first_product, name='sodium', amount=0.82, unit_of_measure='g')
    mommy.make(NutritionFact, product=first_product, name='energyKJ', amount=1830.0, unit_of_measure='KJ')
    mommy.make(NutritionFact, product=first_product, name='energyKcal', amount=436.0, unit_of_measure='Kcal')
    mommy.make(NutritionFact, product=first_product, name='availableCarbohydrate', amount=54.0, unit_of_measure='g')
    first_product.save()

    assert first_product.data_score >= 25
    assert first_product.nutri_score_final is not None

    second_product = mommy.make(Product, gtin=2, product_name_de='Dessert-Tart. Royal 5cm 8 x 23 St.',
                               major_category=major_category, minor_category=minor_category, health_percentage=1,
                               product_size_unit_of_measure='kg', product_size='0.184')
    mommy.make(Matching, eatfit_product=second_product, article_id='Dessert-Tart. Royal 5cm 8 x 23 St.',
               article_type='Migros_long_v1', gtin=2)
    mommy.make(NutritionFact, product=second_product, name='totalFat', amount=25.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=second_product, name='saturatedFat', amount=12.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=second_product, name='totalCarbohydrate', amount=65.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=second_product, name='sugars', amount=21.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=second_product, name='dietaryFiber', amount=2.5, unit_of_measure='g')
    mommy.make(NutritionFact, product=second_product, name='protein', amount=6.2, unit_of_measure='g')
    mommy.make(NutritionFact, product=second_product, name='salt', amount=0.12, unit_of_measure='g')
    mommy.make(NutritionFact, product=second_product, name='sodium', amount=0.05, unit_of_measure='g')
    mommy.make(NutritionFact, product=second_product, name='energyKJ', amount=2162.0, unit_of_measure='KJ')
    mommy.make(NutritionFact, product=second_product, name='energyKcal', amount=516.0, unit_of_measure='Kcal')
    mommy.make(NutritionFact, product=second_product, name='availableCarbohydrate', amount=65.0, unit_of_measure='g')
    second_product.save()

    assert second_product.data_score >= 25
    assert second_product.nutri_score_final is not None


    third_product = mommy.make(Product, gtin=3, product_name_de='Mini Hüppen 1kg ca. 650 Stück',
                                major_category=major_category, minor_category=minor_category, health_percentage=1,
                                product_size_unit_of_measure='kg', product_size='1')
    mommy.make(Matching, eatfit_product=third_product, article_id='Mini Hüppen 1kg ca. 650 Stück',
               article_type='Migros_long_v1', gtin=3)
    mommy.make(NutritionFact, product=third_product, name='totalFat', amount=9.1, unit_of_measure='g')
    mommy.make(NutritionFact, product=third_product, name='saturatedFat', amount=4.6, unit_of_measure='g')
    mommy.make(NutritionFact, product=third_product, name='totalCarbohydrate', amount=80.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=third_product, name='sugars', amount=31.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=third_product, name='dietaryFiber', amount=2.9, unit_of_measure='g')
    mommy.make(NutritionFact, product=third_product, name='protein', amount=8.4, unit_of_measure='g')
    mommy.make(NutritionFact, product=third_product, name='salt', amount=0.68, unit_of_measure='g')
    mommy.make(NutritionFact, product=third_product, name='sodium', amount=0.21, unit_of_measure='g')
    mommy.make(NutritionFact, product=third_product, name='energyKJ', amount=1818.0, unit_of_measure='KJ')
    mommy.make(NutritionFact, product=third_product, name='energyKcal', amount=431.0, unit_of_measure='Kcal')
    mommy.make(NutritionFact, product=third_product, name='availableCarbohydrate', amount=77.0, unit_of_measure='g')
    third_product.save()

    assert third_product.data_score >= 25
    assert third_product.nutri_score_final is not None

    fourth_product = mommy.make(Product, gtin=4, product_name_de='Alnatura Black Bean Cashew Burger',
                                major_category=major_category, minor_category=minor_category, health_percentage=1,
                                product_size_unit_of_measure='g', product_size='160')
    mommy.make(Matching, eatfit_product=fourth_product, article_id='Alnatura Black Bean Cashew Burger',
               article_type='Migros_long_v1', gtin=4)
    mommy.make(NutritionFact, product=fourth_product, name='totalFat', amount=13.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=fourth_product, name='saturatedFat', amount=4.6, unit_of_measure='g')
    mommy.make(NutritionFact, product=fourth_product, name='totalCarbohydrate', amount=20.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=fourth_product, name='sugars', amount=2.6, unit_of_measure='g')
    mommy.make(NutritionFact, product=fourth_product, name='dietaryFiber', amount=8.7, unit_of_measure='g')
    mommy.make(NutritionFact, product=fourth_product, name='protein', amount=5.9, unit_of_measure='g')
    mommy.make(NutritionFact, product=fourth_product, name='salt', amount=1.2, unit_of_measure='g')
    mommy.make(NutritionFact, product=fourth_product, name='sodium', amount=0.02, unit_of_measure='g')
    mommy.make(NutritionFact, product=fourth_product, name='energyKJ', amount=991.0, unit_of_measure='KJ')
    mommy.make(NutritionFact, product=fourth_product, name='energyKcal', amount=238.0, unit_of_measure='Kcal')
    fourth_product.save()

    assert fourth_product.data_score >= 25
    assert fourth_product.nutri_score_final is not None

    fifth_product = mommy.make(Product, gtin=5, product_name_de='Rindshackfleisch 500g',
                                major_category=major_category, minor_category=minor_category, health_percentage=1,
                                product_size_unit_of_measure='g', product_size='500')
    mommy.make(Matching, eatfit_product=fifth_product, article_id='Rindshackfleisch 500g',
               article_type='Migros_long_v1', gtin=5)
    mommy.make(NutritionFact, product=fifth_product, name='totalFat', amount=12.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=fifth_product, name='saturatedFat', amount=4.6, unit_of_measure='g')
    mommy.make(NutritionFact, product=fifth_product, name='totalCarbohydrate', amount=1.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=fifth_product, name='sugars', amount=2.6, unit_of_measure='g')
    mommy.make(NutritionFact, product=fifth_product, name='dietaryFiber', amount=8.7, unit_of_measure='g')
    mommy.make(NutritionFact, product=fifth_product, name='protein', amount=19.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=fifth_product, name='salt', amount=0.1, unit_of_measure='g')
    mommy.make(NutritionFact, product=fifth_product, name='sodium', amount=0.04, unit_of_measure='g')
    mommy.make(NutritionFact, product=fifth_product, name='energyKJ', amount=780.0, unit_of_measure='KJ')
    mommy.make(NutritionFact, product=fifth_product, name='energyKcal', amount=186.0, unit_of_measure='Kcal')
    fifth_product.save()

    assert fifth_product.data_score >= 25
    assert fifth_product.nutri_score_final is not None

    TEST_DATA_DETAILED['r2n_partner'] = r2n_partner.name
    TEST_DATA_DETAILED['r2n_username'] = r2n_user.r2n_username

    assert User.objects.count() == 1
    assert ReceiptToNutritionPartner.objects.count() == 1
    assert ReceiptToNutritionUser.objects.count() == 1
    assert MajorCategory.objects.count() == 1
    assert MinorCategory.objects.count() == 1
    assert Product.objects.count() == 5
    assert Matching.objects.count() == 5
    assert NutritionFact.objects.count() == 53

    api_client = APIRequestFactory()
    view = views.SendReceiptsView.as_view()
    url = reverse('send-receipts')
    request = api_client.post(url, TEST_DATA_DETAILED, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert NonFoundMatching.objects.count() == 0
    assert DigitalReceipt.objects.count() == 5
    assert RECEIPTS_KEY in response.data
    assert len(response.data[RECEIPTS_KEY]) == 1
    assert response.data[RECEIPTS_KEY][0]['nutriscore_indexed'] == 3
    assert response.data[RECEIPTS_KEY][0]['nutriscore'] == 'C'
