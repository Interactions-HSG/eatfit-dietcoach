from model_mommy import mommy
import pytest
import requests_mock

from django.contrib.auth.models import User
from rest_framework.test import force_authenticate, APIRequestFactory

from NutritionService.models import ErrorLog, Product, NotFoundLog
from NutritionService.views.views import get_products_from_openfood
from openfood_data import OPENFOOD_DATA as CONTENT


def create_user():
    user = User.objects.create_superuser(username='test', email='test@test.com', password='test')
    return user


@pytest.mark.django_db
@requests_mock.Mocker()
def test_import_openfood_success(mock):
    assert NotFoundLog.objects.count() == 0
    assert Product.objects.count() == 0
    assert ErrorLog.objects.count() == 0

    mommy.make(NotFoundLog, gtin=7610827921858)
    mock.get(requests_mock.ANY, content=CONTENT)

    factory = APIRequestFactory()
    request = factory.get('/products/from-openfood/')
    force_authenticate(request, user=create_user())
    view = get_products_from_openfood
    response = view(request)

    assert response.status_code == 200
    assert NotFoundLog.objects.count() == 0
    assert Product.objects.count() == 1
    assert ErrorLog.objects.count() == 0

    test_product = Product.objects.get()

    assert test_product.gtin == 7610827921858
    assert test_product.source == 'Openfood'
    assert test_product.product_size == '150.0'
    assert test_product.product_size_unit_of_measure == 'g'
    assert test_product.serving_size == '0.0'
    assert test_product.product_name_de == u'coop FINE FOOD Erdn\xfcsse ger\xf6stet, mit Wasabi'
    assert test_product.product_name_fr == u'coop FINE FOOD Cacahu\xe8tes grill\xe9es au wasabi'
    assert test_product.product_name_it == u'coop FINE FOOD Arachidi tostate al wasabi'


@pytest.mark.django_db
@requests_mock.Mocker()
def test_import_openfood_failure(mock):
    mommy.make(NotFoundLog, gtin=7610827921858)
    test_product = mommy.make(Product, gtin=7610827921858, source='TRUSTBOX', product_size='9',
                              product_size_unit_of_measure='kg', serving_size='2.5', product_name_de=u'Testprodukt',
                              product_name_fr=u'Produit de test', product_name_it=u'Prodotto di prova')

    assert NotFoundLog.objects.count() == 1
    assert Product.objects.count() == 1
    assert ErrorLog.objects.count() == 0

    mock.get(requests_mock.ANY, content=CONTENT)

    factory = APIRequestFactory()
    request = factory.get('/products/from-openfood/')
    force_authenticate(request, user=create_user())
    view = get_products_from_openfood
    response = view(request)

    assert response.status_code == 200
    assert NotFoundLog.objects.count() == 0
    assert Product.objects.count() == 1
    assert ErrorLog.objects.count() == 1
    assert test_product.gtin == 7610827921858
    assert test_product.source == 'TRUSTBOX'
    assert test_product.product_size == '9'
    assert test_product.product_size_unit_of_measure == 'kg'
    assert test_product.serving_size == '2.5'
    assert test_product.product_name_de == u'Testprodukt'
    assert test_product.product_name_fr == u'Produit de test'
    assert test_product.product_name_it == u'Prodotto di prova'
