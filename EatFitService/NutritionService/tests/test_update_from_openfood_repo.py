from datetime import datetime, timedelta
from model_mommy import mommy
import pytest
import requests_mock

from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework.test import force_authenticate, APIRequestFactory

from NutritionService.models import Product, NutritionFact
from NutritionService.views.views import data_clean_task
from openfood_data import OPENFOOD_DATA as CONTENT


def create_user():
    user = User.objects.create_superuser(username='test', email='test@test.com', password='test')
    return user


@pytest.mark.django_db
@requests_mock.Mocker()
def test_openfood_repo_update_success(mock):

    test_product = mommy.make(Product, gtin=7610827921858, product_size=None, product_size_unit_of_measure=None,
                              product_name_de=None, product_name_fr=None, product_name_it=None,
                              quality_checked=None, automatic_update=True)

    mommy.make(NutritionFact, product=test_product, name='protein', amount=4.1, unit_of_measure='g')

    assert Product.objects.count() == 1
    assert NutritionFact.objects.count() == 1

    mock.get(requests_mock.ANY, content=CONTENT)

    factory = APIRequestFactory()
    request = factory.get('data/data-cleaning/')
    force_authenticate(request, user=create_user())
    view = data_clean_task
    response = view(request)

    updated_product = Product.objects.get(gtin=7610827921858)

    assert response.status_code == 200

    assert updated_product.product_size == '150.0'
    assert updated_product.product_size != test_product.product_size

    assert updated_product.product_size_unit_of_measure == 'g'
    assert updated_product.product_size_unit_of_measure != test_product.product_size_unit_of_measure

    assert updated_product.product_name_de == u'coop FINE FOOD Erdn\xfcsse ger\xf6stet, mit Wasabi'
    assert updated_product.product_name_de != test_product.product_name_de

    assert updated_product.product_name_fr == u'coop FINE FOOD Cacahu\xe8tes grill\xe9es au wasabi'
    assert updated_product.product_name_fr != test_product.product_name_fr

    assert updated_product.product_name_it == u'coop FINE FOOD Arachidi tostate al wasabi'
    assert updated_product.product_name_it != test_product.product_name_it

    assert updated_product.data_score > 0.0
    assert updated_product.data_score != test_product.data_score

    assert updated_product.quality_checked
    assert updated_product.quality_checked != test_product.quality_checked

    assert NutritionFact.objects.filter(product=test_product, name='protein', amount=4.1, unit_of_measure='g').exists()
    assert NutritionFact.objects.count() == 4


@pytest.mark.django_db
@requests_mock.Mocker()
def test_openfood_repo_update_failure(mock):

    date_checked = datetime.now() - timedelta(days=32)

    test_product = mommy.make(Product, gtin=7610827921858, product_size='150.0', product_size_unit_of_measure='g',
                              product_name_de=u'coop FINE FOOD Erdn\xfcsse ger\xf6stet, mit Wasabi',
                              product_name_fr=u'coop FINE FOOD Cacahu\xe8tes grill\xe9es au wasabi',
                              product_name_it=u'coop FINE FOOD Arachidi tostate al wasabi',
                              automatic_update=False, quality_checked=date_checked)

    mommy.make(NutritionFact, product=test_product, name='protein', amount=4.1, unit_of_measure='g')

    assert Product.objects.count() == 1
    assert NutritionFact.objects.count() == 1

    mock.get(requests_mock.ANY, content=CONTENT)

    factory = APIRequestFactory()
    request = factory.get('data/data-cleaning/')
    force_authenticate(request, user=create_user())
    view = data_clean_task
    response = view(request)

    updated_product = Product.objects.get(gtin=7610827921858)

    assert response.status_code == 200

    assert updated_product.product_size == '150.0'
    assert updated_product.product_size == test_product.product_size

    assert updated_product.product_size_unit_of_measure == 'g'
    assert updated_product.product_size_unit_of_measure == test_product.product_size_unit_of_measure

    assert updated_product.product_name_de == u'coop FINE FOOD Erdn\xfcsse ger\xf6stet, mit Wasabi'
    assert updated_product.product_name_de == test_product.product_name_de

    assert updated_product.product_name_fr == u'coop FINE FOOD Cacahu\xe8tes grill\xe9es au wasabi'
    assert updated_product.product_name_fr == test_product.product_name_fr

    assert updated_product.product_name_it == u'coop FINE FOOD Arachidi tostate al wasabi'
    assert updated_product.product_name_it == test_product.product_name_it

    assert updated_product.data_score > 0.0
    assert updated_product.data_score == test_product.data_score

    assert updated_product.quality_checked
    assert updated_product.quality_checked.replace(tzinfo=None) == test_product.quality_checked.replace(tzinfo=None)

    assert NutritionFact.objects.filter(product=test_product, name='protein', amount=4.1, unit_of_measure='g').exists()
    assert NutritionFact.objects.count() == 1
