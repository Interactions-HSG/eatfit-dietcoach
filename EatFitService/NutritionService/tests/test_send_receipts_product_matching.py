import pytest
from model_mommy import mommy

from django.db.models import F, Func
from django.contrib.auth.models import User

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.reverse import reverse
from rest_framework import status

from NutritionService.views import views
from NutritionService.models import ErrorLog, NonFoundMatching, DigitalReceipt, ReceiptToNutritionUser, \
    ReceiptToNutritionPartner, Product, Matching
from send_receipts_data import TEST_DATA

TEST_USER_AND_PASSWORD = 'test'
PARTNER_AND_USER_NAME = 'Kevin'
URL_REVERSE = 'send-receipts'
ARTICLE_ID = 'Apfel Braeburn'
ARTICLE_TYPE = 'Migros_long_v1'
PRICE = 1.85

@pytest.mark.django_db
def test_matching_non_found_inexistent():

    assert User.objects.count() == 0
    assert ReceiptToNutritionPartner.objects.count() == 0
    assert ReceiptToNutritionUser.objects.count() == 0
    assert Matching.objects.count() == 0
    assert NonFoundMatching.objects.count() == 0

    user = User.objects.create_user(username=TEST_USER_AND_PASSWORD, password=TEST_USER_AND_PASSWORD)
    r2n_partner = mommy.make(ReceiptToNutritionPartner, user=user, name=PARTNER_AND_USER_NAME)
    r2n_user = mommy.make(ReceiptToNutritionUser, r2n_partner=r2n_partner, r2n_username=PARTNER_AND_USER_NAME)

    TEST_DATA['r2n_partner'] = r2n_partner.name
    TEST_DATA['r2n_username'] = r2n_user.r2n_username

    assert User.objects.count() == 1
    assert ReceiptToNutritionPartner.objects.count() == 1
    assert ReceiptToNutritionUser.objects.count() == 1

    api_client = APIRequestFactory()
    view = views.SendReceiptsView.as_view()
    url = reverse(URL_REVERSE)
    request = api_client.post(url, TEST_DATA, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert ReceiptToNutritionUser.objects.count() == 1
    assert NonFoundMatching.objects.count() == 1


@pytest.mark.django_db
def test_matching_non_found_exists():

    assert User.objects.count() == 0
    assert ReceiptToNutritionPartner.objects.count() == 0
    assert ReceiptToNutritionUser.objects.count() == 0
    assert Matching.objects.count() == 0
    assert NonFoundMatching.objects.count() == 0

    user = User.objects.create_user(username=TEST_USER_AND_PASSWORD, password=TEST_USER_AND_PASSWORD)
    r2n_partner = mommy.make(ReceiptToNutritionPartner, user=user, name=PARTNER_AND_USER_NAME)
    r2n_user = mommy.make(ReceiptToNutritionUser, r2n_partner=r2n_partner, r2n_username=PARTNER_AND_USER_NAME)
    mommy.make(NonFoundMatching, article_id=ARTICLE_ID, article_type=ARTICLE_TYPE, counter=0)

    TEST_DATA['r2n_partner'] = r2n_partner.name
    TEST_DATA['r2n_username'] = r2n_user.r2n_username

    assert User.objects.count() == 1
    assert ReceiptToNutritionPartner.objects.count() == 1
    assert ReceiptToNutritionUser.objects.count() == 1
    assert NonFoundMatching.objects.count() == 1

    api_client = APIRequestFactory()
    view = views.SendReceiptsView.as_view()
    url = reverse(URL_REVERSE)
    request = api_client.post(url, TEST_DATA, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert NonFoundMatching.objects.count() == 1

    test_object = NonFoundMatching.objects.get(article_id=ARTICLE_ID, article_type=ARTICLE_TYPE)

    assert test_object.counter == 1


@pytest.mark.django_db
def test_matching_multiple_price_does_not_exist():

    assert User.objects.count() == 0
    assert ReceiptToNutritionPartner.objects.count() == 0
    assert ReceiptToNutritionUser.objects.count() == 0
    assert Matching.objects.count() == 0
    assert NonFoundMatching.objects.count() == 0
    assert Product.objects.count() == 0

    user = User.objects.create_user(username=TEST_USER_AND_PASSWORD, password=TEST_USER_AND_PASSWORD )
    r2n_partner = mommy.make(ReceiptToNutritionPartner, user=user, name=PARTNER_AND_USER_NAME)
    r2n_user = mommy.make(ReceiptToNutritionUser, r2n_partner=r2n_partner, r2n_username=PARTNER_AND_USER_NAME)
    test_product = mommy.make(Product)
    mommy.make(Matching, article_id=ARTICLE_ID, article_type=ARTICLE_TYPE, gtin=0,
               eatfit_product=test_product, price_per_unit=None)
    mommy.make(Matching, article_id=ARTICLE_ID, article_type=ARTICLE_TYPE, gtin=1,
               eatfit_product=test_product, price_per_unit=None)

    TEST_DATA['r2n_partner'] = r2n_partner.name
    TEST_DATA['r2n_username'] = r2n_user.r2n_username

    assert User.objects.count() == 1
    assert ReceiptToNutritionPartner.objects.count() == 1
    assert ReceiptToNutritionUser.objects.count() == 1
    assert Matching.objects.count() == 2
    assert Product.objects.count() == 1

    api_client = APIRequestFactory()
    view = views.SendReceiptsView.as_view()
    url = reverse(URL_REVERSE)
    request = api_client.post(url, TEST_DATA, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert NonFoundMatching.objects.count() == 0

    test_object = Matching.objects.filter(article_id=ARTICLE_ID,
                                          article_type=ARTICLE_TYPE,
                                          price_per_unit__isnull=False).annotate(
        absolute_price_difference=Func(F('price_per_unit') - PRICE, function='ABS')).order_by(
        'absolute_price_difference').first()

    assert test_object is None

    test_object = Matching.objects.filter().first()

    assert test_object.gtin == 0


@pytest.mark.django_db
def test_matching_multiple_some_prices_exist():

    assert User.objects.count() == 0
    assert ReceiptToNutritionPartner.objects.count() == 0
    assert ReceiptToNutritionUser.objects.count() == 0
    assert Matching.objects.count() == 0
    assert NonFoundMatching.objects.count() == 0
    assert Product.objects.count() == 0

    user = User.objects.create_user(username=TEST_USER_AND_PASSWORD, password=TEST_USER_AND_PASSWORD )
    r2n_partner = mommy.make(ReceiptToNutritionPartner, user=user, name=PARTNER_AND_USER_NAME)
    r2n_user = mommy.make(ReceiptToNutritionUser, r2n_partner=r2n_partner, r2n_username=PARTNER_AND_USER_NAME)
    test_product = mommy.make(Product)
    mommy.make(Matching, article_id=ARTICLE_ID, article_type=ARTICLE_TYPE, gtin=0,
               eatfit_product=test_product, price_per_unit=None)
    mommy.make(Matching, article_id=ARTICLE_ID, article_type=ARTICLE_TYPE, gtin=1,
               eatfit_product=test_product, price_per_unit=10)

    TEST_DATA['r2n_partner'] = r2n_partner.name
    TEST_DATA['r2n_username'] = r2n_user.r2n_username

    assert User.objects.count() == 1
    assert ReceiptToNutritionPartner.objects.count() == 1
    assert ReceiptToNutritionUser.objects.count() == 1
    assert Matching.objects.count() == 2
    assert Product.objects.count() == 1

    api_client = APIRequestFactory()
    view = views.SendReceiptsView.as_view()
    url = reverse(URL_REVERSE)
    request = api_client.post(url, TEST_DATA, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert NonFoundMatching.objects.count() == 0

    test_object = Matching.objects.filter(article_id=ARTICLE_ID,
                                          article_type=ARTICLE_TYPE,
                                          price_per_unit__isnull=False).annotate(
                absolute_price_difference=Func(F('price_per_unit') - PRICE, function='ABS')).order_by(
                'absolute_price_difference').first()

    assert test_object != Matching.objects.filter().first()
    assert test_object.gtin == 1


@pytest.mark.django_db
def test_matching_multiple_by_price():

    assert User.objects.count() == 0
    assert ReceiptToNutritionPartner.objects.count() == 0
    assert ReceiptToNutritionUser.objects.count() == 0
    assert Matching.objects.count() == 0
    assert NonFoundMatching.objects.count() == 0
    assert Product.objects.count() == 0

    user = User.objects.create_user(username=TEST_USER_AND_PASSWORD, password=TEST_USER_AND_PASSWORD)
    r2n_partner = mommy.make(ReceiptToNutritionPartner, user=user, name=PARTNER_AND_USER_NAME)
    r2n_user = mommy.make(ReceiptToNutritionUser, r2n_partner=r2n_partner, r2n_username=PARTNER_AND_USER_NAME)
    test_product = mommy.make(Product)
    mommy.make(Matching, article_id=ARTICLE_ID, article_type=ARTICLE_TYPE, gtin=0,
               eatfit_product=test_product, price_per_unit=10)
    mommy.make(Matching, article_id=ARTICLE_ID, article_type=ARTICLE_TYPE, gtin=1,
               eatfit_product=test_product, price_per_unit=5)

    TEST_DATA['r2n_partner'] = r2n_partner.name
    TEST_DATA['r2n_username'] = r2n_user.r2n_username

    assert User.objects.count() == 1
    assert ReceiptToNutritionPartner.objects.count() == 1
    assert ReceiptToNutritionUser.objects.count() == 1
    assert Matching.objects.count() == 2
    assert Product.objects.count() == 1

    api_client = APIRequestFactory()
    view = views.SendReceiptsView.as_view()
    url = reverse(URL_REVERSE)
    request = api_client.post(url, TEST_DATA, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert NonFoundMatching.objects.count() == 0

    test_object = Matching.objects.filter(article_id=ARTICLE_ID,
                                          article_type=ARTICLE_TYPE).annotate(
        absolute_price_difference=Func(F('price_per_unit') - PRICE, function='ABS')).order_by(
        'absolute_price_difference').first()

    assert test_object != Matching.objects.filter().first()
    assert test_object.gtin == 1


@pytest.mark.django_db
def test_matching_valid():

    assert User.objects.count() == 0
    assert ReceiptToNutritionPartner.objects.count() == 0
    assert ReceiptToNutritionUser.objects.count() == 0
    assert Matching.objects.count() == 0
    assert NonFoundMatching.objects.count() == 0
    assert Product.objects.count() == 0

    user = User.objects.create_user(username=TEST_USER_AND_PASSWORD, password=TEST_USER_AND_PASSWORD)
    r2n_partner = mommy.make(ReceiptToNutritionPartner, user=user, name=PARTNER_AND_USER_NAME)
    r2n_user = mommy.make(ReceiptToNutritionUser, r2n_partner=r2n_partner, r2n_username=PARTNER_AND_USER_NAME)
    test_product = mommy.make(Product)
    mommy.make(Matching, article_id=ARTICLE_ID, article_type=ARTICLE_TYPE, eatfit_product=test_product)

    TEST_DATA['r2n_partner'] = r2n_partner.name
    TEST_DATA['r2n_username'] = r2n_user.r2n_username

    assert User.objects.count() == 1
    assert ReceiptToNutritionPartner.objects.count() == 1
    assert ReceiptToNutritionUser.objects.count() == 1
    assert Matching.objects.count() == 1
    assert Product.objects.count() == 1

    api_client = APIRequestFactory()
    view = views.SendReceiptsView.as_view()
    url = reverse(URL_REVERSE)
    request = api_client.post(url, TEST_DATA, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert NonFoundMatching.objects.count() == 0
