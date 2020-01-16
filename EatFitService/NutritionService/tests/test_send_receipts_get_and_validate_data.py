import pytest
from model_mommy import mommy

from django.contrib.auth.models import User

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.reverse import reverse
from rest_framework import status

from NutritionService.views import views
from NutritionService.views.errors import SendReceiptsErrors
from NutritionService.models import ReceiptToNutritionUser, ReceiptToNutritionPartner
from send_receipts_data import TEST_DATA

ERROR_KEY = 'error'
errors = SendReceiptsErrors()


@pytest.mark.django_db
def test_user_partner_exists():

    ERROR_MESSAGE = 'You must be a partner to use this API'

    assert User.objects.count() == 0
    assert ReceiptToNutritionPartner.objects.count() == 0

    user = User.objects.create_user(username='test', password='test')

    assert User.objects.count() == 1

    TEST_DATA['r2n_partner'] = ''
    TEST_DATA['r2n_username'] = ''

    api_client = APIRequestFactory()
    view = views.SendReceiptsView.as_view()
    url = reverse('send-receipts')
    request = api_client.post(url, TEST_DATA, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert ERROR_KEY in response.data
    assert response.data[ERROR_KEY] == errors.PARTNER_DOES_NOT_EXIST


@pytest.mark.django_db
def test_serializer_invalid():

    assert User.objects.count() == 0
    assert ReceiptToNutritionPartner.objects.count() == 0

    user = User.objects.create_user(username='test', password='test')
    mommy.make(ReceiptToNutritionPartner, user=user)

    assert User.objects.count() == 1
    assert ReceiptToNutritionPartner.objects.count() == 1

    TEST_DATA['r2n_partner'] = ''
    TEST_DATA['r2n_username'] = ''

    api_client = APIRequestFactory()
    view = views.SendReceiptsView.as_view()
    url = reverse('send-receipts')
    request = api_client.post(url, TEST_DATA, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_user_partner_inexistent():

    assert User.objects.count() == 0
    assert ReceiptToNutritionPartner.objects.count() == 0
    assert ReceiptToNutritionUser.objects.count() == 0

    user = User.objects.create_user(username='test', password='test')
    mommy.make(ReceiptToNutritionPartner, user=user)

    TEST_DATA['r2n_partner'] = 'Kevin'
    TEST_DATA['r2n_username'] = 'Kevin'

    assert User.objects.count() == 1
    assert ReceiptToNutritionPartner.objects.count() == 1
    assert ReceiptToNutritionUser.objects.count() == 0

    api_client = APIRequestFactory()
    view = views.SendReceiptsView.as_view()
    url = reverse('send-receipts')
    request = api_client.post(url, TEST_DATA, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_user_partner_activity():

    assert User.objects.count() == 0
    assert ReceiptToNutritionPartner.objects.count() == 0
    assert ReceiptToNutritionUser.objects.count() == 0

    user = User.objects.create_user(username='test', password='test')
    r2n_partner = mommy.make(ReceiptToNutritionPartner, user=user, name='Kevin')
    r2n_user = mommy.make(ReceiptToNutritionUser, r2n_partner=r2n_partner, r2n_username='Kevin', r2n_user_active=False)

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

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert ERROR_KEY in response.data
    assert response.data[ERROR_KEY] == errors.USER_INACTIVE
