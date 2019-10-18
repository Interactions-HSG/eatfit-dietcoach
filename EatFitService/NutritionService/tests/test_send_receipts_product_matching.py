import pytest
from model_mommy import mommy

from django.contrib.auth.models import User

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.reverse import reverse
from rest_framework import status

from NutritionService.views import views
from NutritionService.models import ErrorLog, NonFoundMatching, DigitalReceipt, ReceiptToNutritionUser, \
    ReceiptToNutritionPartner, Product, Matching
from send_receipts_data import TEST_DATA


@pytest.mark.django_db
def test_matching_non_found_inexistent():

    assert User.objects.count() == 0
    assert ReceiptToNutritionPartner.objects.count() == 0
    assert ReceiptToNutritionUser.objects.count() == 0
    assert Matching.objects.count() == 0
    assert NonFoundMatching.objects.count() == 0

    user = User.objects.create_user(username='test', password='test')
    r2n_partner = mommy.make(ReceiptToNutritionPartner, user=user, name='Kevin')
    r2n_user = mommy.make(ReceiptToNutritionUser, r2n_partner=r2n_partner, r2n_username='Kevin')

    TEST_DATA['r2n_partner'] = r2n_partner.name
    TEST_DATA['r2n_username'] = r2n_user.r2n_username

    assert User.objects.count() == 1
    assert ReceiptToNutritionPartner.objects.count() == 1
    assert ReceiptToNutritionUser.objects.count() == 1

    api_client = APIRequestFactory()
    view = views.SendReceiptsView.as_view()
    url = reverse('send-receipts')
    request = api_client.post(url, TEST_DATA, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_201_CREATED
    assert ReceiptToNutritionUser.objects.count() == 1
    assert NonFoundMatching.objects.count() == 1


@pytest.mark.django_db
def test_matching_non_found_exists():

    assert User.objects.count() == 0
    assert ReceiptToNutritionPartner.objects.count() == 0
    assert ReceiptToNutritionUser.objects.count() == 0
    assert Matching.objects.count() == 0
    assert NonFoundMatching.objects.count() == 0

    user = User.objects.create_user(username='test', password='test')
    r2n_partner = mommy.make(ReceiptToNutritionPartner, user=user, name='Kevin')
    r2n_user = mommy.make(ReceiptToNutritionUser, r2n_partner=r2n_partner, r2n_username='Kevin')
    mommy.make(NonFoundMatching, article_id='Apfel Braeburn', article_type='Migros_long_v1')

    TEST_DATA['r2n_partner'] = r2n_partner.name
    TEST_DATA['r2n_username'] = r2n_user.r2n_username

    assert User.objects.count() == 1
    assert ReceiptToNutritionPartner.objects.count() == 1
    assert ReceiptToNutritionUser.objects.count() == 1
    assert NonFoundMatching.objects.count() == 1

    api_client = APIRequestFactory()
    view = views.SendReceiptsView.as_view()
    url = reverse('send-receipts')
    request = api_client.post(url, TEST_DATA, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_201_CREATED
    assert NonFoundMatching.objects.count() == 1

    test_object = NonFoundMatching.objects.get(article_id='Apfel Braeburn', article_type='Migros_long_v1')

    assert test_object.counter == 1


@pytest.mark.django_db
def test_matching_multiple():

    assert User.objects.count() == 0
    assert ReceiptToNutritionPartner.objects.count() == 0
    assert ReceiptToNutritionUser.objects.count() == 0
    assert Matching.objects.count() == 0
    assert NonFoundMatching.objects.count() == 0
    assert Product.objects.count() == 0

    user = User.objects.create_user(username='test', password='test')
    r2n_partner = mommy.make(ReceiptToNutritionPartner, user=user, name='Kevin')
    r2n_user = mommy.make(ReceiptToNutritionUser, r2n_partner=r2n_partner, r2n_username='Kevin')
    test_product = mommy.make(Product)
    mommy.make(Matching, article_id='Apfel Braeburn', article_type='Migros_long_v1', gtin=0,
               eatfit_product=test_product)
    mommy.make(Matching, article_id='Apfel Braeburn', article_type='Migros_long_v1', gtin=1,
               eatfit_product=test_product)

    TEST_DATA['r2n_partner'] = r2n_partner.name
    TEST_DATA['r2n_username'] = r2n_user.r2n_username

    assert User.objects.count() == 1
    assert ReceiptToNutritionPartner.objects.count() == 1
    assert ReceiptToNutritionUser.objects.count() == 1
    assert Matching.objects.count() == 2
    assert Product.objects.count() == 1

    api_client = APIRequestFactory()
    view = views.SendReceiptsView.as_view()
    url = reverse('send-receipts')
    request = api_client.post(url, TEST_DATA, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_201_CREATED
    assert NonFoundMatching.objects.count() == 0

    test_object = Matching.objects.filter().first()

    assert test_object.gtin == 0


@pytest.mark.django_db
def test_matching_valid():

    assert User.objects.count() == 0
    assert ReceiptToNutritionPartner.objects.count() == 0
    assert ReceiptToNutritionUser.objects.count() == 0
    assert Matching.objects.count() == 0
    assert NonFoundMatching.objects.count() == 0
    assert Product.objects.count() == 0

    user = User.objects.create_user(username='test', password='test')
    r2n_partner = mommy.make(ReceiptToNutritionPartner, user=user, name='Kevin')
    r2n_user = mommy.make(ReceiptToNutritionUser, r2n_partner=r2n_partner, r2n_username='Kevin')
    test_product = mommy.make(Product)
    mommy.make(Matching, article_id='Apfel Braeburn', article_type='Migros_long_v1', eatfit_product=test_product)

    TEST_DATA['r2n_partner'] = r2n_partner.name
    TEST_DATA['r2n_username'] = r2n_user.r2n_username

    assert User.objects.count() == 1
    assert ReceiptToNutritionPartner.objects.count() == 1
    assert ReceiptToNutritionUser.objects.count() == 1
    assert Matching.objects.count() == 1
    assert Product.objects.count() == 1

    api_client = APIRequestFactory()
    view = views.SendReceiptsView.as_view()
    url = reverse('send-receipts')
    request = api_client.post(url, TEST_DATA, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_201_CREATED
    assert NonFoundMatching.objects.count() == 0
