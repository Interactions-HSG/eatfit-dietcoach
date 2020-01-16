# coding=utf-8
from model_mommy import mommy
import pytest
from requests_mock import ANY

from django.contrib.auth.models import User
from rest_framework.test import force_authenticate, APIRequestFactory

from NutritionService.models import MINERAL_WATER, ErrorLog, Product, NotFoundLog, MinorCategory, MajorCategory
from NutritionService.views.views import get_products_from_openfood
from openfood_data import OPENFOOD_DATA as CONTENT


def create_user():
    user = User.objects.create_superuser(username='test', email='test@test.com', password='test')
    return user


@pytest.mark.django_db
def test_import_openfood_success(requests_mock):
    assert NotFoundLog.objects.count() == 0
    assert Product.objects.count() == 0
    assert ErrorLog.objects.count() == 0

    mommy.make(NotFoundLog, gtin=7610827921858)
    requests_mock.get(ANY, text=CONTENT)

    factory = APIRequestFactory()
    request = factory.get('/products/from-openfood/')
    force_authenticate(request, user=create_user())
    view = get_products_from_openfood
    response = view(request)

    assert response.status_code == 200
    assert NotFoundLog.objects.count() == 0
    assert Product.objects.count() == 1
    assert ErrorLog.objects.exclude(reporting_app='Eatfit_NS').count() == 0

    test_product = Product.objects.get()

    assert test_product.gtin == 7610827921858
    assert test_product.source == 'Openfood'
    assert test_product.product_size == '150.0'
    assert test_product.product_size_unit_of_measure == 'g'
    assert test_product.serving_size == '0.0'
    assert test_product.product_name_de == 'coop FINE FOOD Erdnüsse geröstet, mit Wasabi'
    assert test_product.product_name_fr == 'coop FINE FOOD Cacahuètes grillées au wasabi'
    assert test_product.product_name_it == 'coop FINE FOOD Arachidi tostate al wasabi'


@pytest.mark.django_db
def test_import_openfood_failure(requests_mock):
    assert MajorCategory.objects.count() == 0
    assert MinorCategory.objects.count() == 0
    assert NotFoundLog.objects.count() == 0

    major_category = mommy.make(MajorCategory, pk=16)
    minor_category = mommy.make(MinorCategory, pk=82, category_major=major_category, nutri_score_category=MINERAL_WATER)
    mommy.make(NotFoundLog, gtin=7610827921858)
    test_product = mommy.make(Product, gtin=7610827921858, source='TRUSTBOX', product_size='9',
                              product_size_unit_of_measure='kg', serving_size='2.5', product_name_de='Testprodukt',
                              product_name_fr='Produit de test', product_name_it='Prodotto di prova',
                              minor_category=minor_category)

    assert NotFoundLog.objects.count() == 1
    assert MajorCategory.objects.count() == 1
    assert MinorCategory.objects.count() == 1
    assert Product.objects.count() == 1
    assert ErrorLog.objects.count() == 0

    requests_mock.get(ANY, text=CONTENT)

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
    assert test_product.product_name_de == 'Testprodukt'
    assert test_product.product_name_fr == 'Produit de test'
    assert test_product.product_name_it == 'Prodotto di prova'
