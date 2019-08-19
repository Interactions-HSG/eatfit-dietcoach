from model_mommy import mommy
import pytest
import requests_mock

from django.test import RequestFactory
from django.contrib.auth.models import User
from rest_framework.test import force_authenticate

from NutritionService.models import ErrorLog, Product, NotFoundLog
from NutritionService.views.views import get_products_from_openfood
from openfood_data import OPENFOOD_DATA as CONTENT


def create_user():
    user = User.objects.create_superuser(username='test', email='test@test.com', password='test')
    return user


@pytest.mark.django_db
@requests_mock.Mocker()
def test_import_openfood_success(mock):
    mommy.make(NotFoundLog, gtin=7610827921858)

    mock.get(requests_mock.ANY, content=CONTENT)

    factory = RequestFactory()
    request = factory.get('/products/from-openfood/')
    force_authenticate(request, user=create_user())
    view = get_products_from_openfood
    response = view(request)

    assert response.status_code == 200
    assert NotFoundLog.objects.count() == 0
    assert Product.objects.count() == 1
    assert ErrorLog.objects.count() == 0


@pytest.mark.django_db
@requests_mock.Mocker()
def test_import_openfood_failure(mock):
    mommy.make(NotFoundLog, gtin=7610827921858)
    mommy.make(Product, gtin=7610827921858)

    mock.get(requests_mock.ANY, content=CONTENT)

    factory = RequestFactory()
    request = factory.get('/products/from-openfood/')
    force_authenticate(request, user=create_user())
    view = get_products_from_openfood
    response = view(request)

    assert response.status_code == 200
    assert NotFoundLog.objects.count() == 0
    assert Product.objects.count() == 1
    assert ErrorLog.objects.count() == 1



