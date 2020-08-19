import json

import pytest
from model_mommy import mommy
from rest_framework.test import APIRequestFactory, force_authenticate

from NutritionService.models import ReceiptToNutritionPartner, ReceiptToNutritionUser, Matching, Product, \
    NutriScoreFacts, MinorCategory
from NutritionService.views import views
from NutritionService import models
from NutritionService.views.views import BasketDetailedAnalysisView
from django.contrib.auth.models import User

@pytest.fixture
def fvpn_test_data():
    return {
        "r2n_partner": "Kevin",
        "r2n_username": "Kevin",
        "receipts": [
            {
                "receipt_datetime": "2020-02-20T11:49:59Z",
                "business_unit": "Migros",
                "items": [
                    {
                        "article_id": "Coop Gruyère Reibkäse 130g",
                        "article_type": "Coop_long_v1",
                        "quantity": 10.000,
                        "quantity_unit": "kg",
                        "price": "3.90",
                        "price_currency": "CHF"
                    },
                    {
                        "article_id": "Saladbowl Tuna",
                        "article_type": "Migros_long_v1",
                        "quantity": 1.000,
                        "quantity_unit": "kg",
                        "price": "3.90",
                        "price_currency": "CHF"
                    }
                ]
            }
        ]
    }

@pytest.fixture
def user():
    user = User.objects.create_user(username='test', password='test')
    r2n_partner = mommy.make(ReceiptToNutritionPartner, user=user, name='Kevin')
    mommy.make(ReceiptToNutritionUser, r2n_partner=r2n_partner, r2n_username='Kevin')

    return user


@pytest.fixture
def init_products():
    cat1 = mommy.make(MinorCategory)
    test_cheese_product = mommy.make(Product, product_name_de='Coop Gruyère Reibkäse 130g', health_percentage=0,
                                     nutri_score_by_manufacturer=Product.D,
                                     minor_category=cat1)
    mommy.make(Matching, eatfit_product=test_cheese_product, article_id='Coop Gruyère Reibkäse 130g',
               article_type='Coop_long_v1')
    mommy.make(
        NutriScoreFacts,
        ofcom_p_fvpn=0,
        product=test_cheese_product,
        ofcom_n_energy_kj=3)

    cat2 = mommy.make(MinorCategory)
    test_salad_product = mommy.make(Product, product_name_de='Saladbowl Tuna', health_percentage=58,
                                    nutri_score_by_manufacturer=Product.A,
                                    minor_category=cat2)
    mommy.make(Matching, eatfit_product=test_salad_product, article_id='Saladbowl Tuna',
               article_type='Migros_long_v1')
    mommy.make(
        NutriScoreFacts,
        ofcom_p_fvpn=5,
        product=test_salad_product,
        ofcom_n_energy_kj=2)


@pytest.mark.django_db
def test_fvpn_calculation(fvpn_test_data, init_products, user):

    factory = APIRequestFactory()
    request = factory.post('/receipt2nutrition/basket-detailed-analysis/', fvpn_test_data, format='json')
    force_authenticate(request, user=user)
    response = BasketDetailedAnalysisView.as_view()(request)
    response_data = json.loads(response.rendered_content)

    assert response_data['overall_purchase_statistics']['number_of_detected_products'] == 2

    assert any(d['nutrient'] == 'FVPN' and d['ofcom_point_average'] > 0.454 and d['ofcom_point_average'] < 0.455 for d in
               response_data['nutrient_sources']['positive_nutrients'])

    assert any(d['nutrient'] == 'FVPN' and d['amount'] == 580 for d in
               response_data['nutrient_sources']['positive_nutrients'])

@pytest.mark.django_db
def test_nutri_score(fvpn_test_data, init_products, user):
    factory = APIRequestFactory()
    request = factory.post('/receipt2nutrition/basket-detailed-analysis/', fvpn_test_data, format='json')
    force_authenticate(request, user=user)
    response = BasketDetailedAnalysisView.as_view()(request)
    response_data = json.loads(response.rendered_content)

    assert response_data['nutri_score_by_basket'][0]['nutri_score_average'] == "D"
    assert 1.773 > response_data['nutri_score_by_basket'][0]['nutri_score_indexed'] > 1.772

@pytest.mark.django_db
def test_category_amount(fvpn_test_data, init_products, user):
    factory = APIRequestFactory()
    request = factory.post('/receipt2nutrition/basket-detailed-analysis/', fvpn_test_data, format='json')
    force_authenticate(request, user=user)
    response = BasketDetailedAnalysisView.as_view()(request)
    response_data = json.loads(response.rendered_content)

    assert len(response_data['distribution_by_minor_category']) == 2
    assert any(d['amount'] == 10000.0 for d in
               response_data['distribution_by_minor_category'])
    assert any(d['amount'] == 1000.0 for d in
               response_data['distribution_by_minor_category'])

@pytest.mark.django_db
def test_unknown_products(fvpn_test_data, user):
    factory = APIRequestFactory()
    request = factory.post('/receipt2nutrition/basket-detailed-analysis/', fvpn_test_data, format='json')
    force_authenticate(request, user=user)
    response = BasketDetailedAnalysisView.as_view()(request)
    response_data = json.loads(response.rendered_content)

    assert response_data['nutri_score_by_basket'][0]['nutri_score_average'] == 'unknown'
    assert response_data['nutri_score_by_basket'][0]['nutri_score_indexed'] == 'unknown'

    assert response_data['overall_purchase_statistics']['number_of_products'] == 2
    assert response_data['overall_purchase_statistics']['number_of_detected_products'] == 0
    assert response_data['overall_purchase_statistics']['total_weight_of_detected_products'] == 0
