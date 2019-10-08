import json
from model_mommy import mommy
import pytest

from django.contrib.auth.models import User
from rest_framework.test import force_authenticate, APIRequestFactory

from NutritionService.models import MINERAL_WATER, BEVERAGE, FOOD, Product, MinorCategory, MajorCategory, NutritionFact, MarketRegion, Retailer
from NutritionService.views.views import get_better_products_gtin


def create_user():
    user = User.objects.create_superuser(username='test', email='test@test.com', password='test')
    return user


@pytest.mark.django_db
def test_get_better_products_sort_by_ofcom():

    assert MajorCategory.objects.count() == 0
    assert MinorCategory.objects.count() == 0
    assert Product.objects.count() == 0

    # Major Category

    maj_cat_16 = mommy.make(MajorCategory, pk=16)

    # Minor Category

    min_cat_82 = mommy.make(MinorCategory, pk=84, category_major=maj_cat_16, nutri_score_category=FOOD)

    # Products
    first_product = mommy.make(Product, gtin=4004980511200, minor_category=min_cat_82)

    mommy.make(NutritionFact, product=first_product, name='dietaryFiber', amount=8.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=first_product, name='sugars', amount=0.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=first_product, name='saturatedFat', amount=0.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=first_product, name='energyKJ', amount=0.0, unit_of_measure='kj')
    mommy.make(NutritionFact, product=first_product, name='sodium', amount=0.0, unit_of_measure='mg')

    first_product.save()

    assert first_product.ofcom_value == -5

    second_product = mommy.make(Product, gtin=29000076501, minor_category=min_cat_82)

    mommy.make(NutritionFact, product=second_product, name='sugars', amount=9.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=second_product, name='saturatedFat', amount=2.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=second_product, name='energyKJ', amount=670.0, unit_of_measure='kj')
    mommy.make(NutritionFact, product=second_product, name='sodium', amount=180.0, unit_of_measure='mg')

    second_product.save()

    assert second_product.ofcom_value == 4

    third_product = mommy.make(Product, gtin=30111187612, minor_category=min_cat_82)

    mommy.make(NutritionFact, product=third_product, name='sugars', amount=0.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=third_product, name='saturatedFat', amount=0.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=third_product, name='energyKJ', amount=0.0, unit_of_measure='kj')
    mommy.make(NutritionFact, product=third_product, name='sodium', amount=0.0, unit_of_measure='mg')

    third_product.save()

    assert third_product.ofcom_value == 0
    assert MajorCategory.objects.count() == 1
    assert MinorCategory.objects.count() == 1
    assert Product.objects.count() == 3

    factory = APIRequestFactory()
    view = get_better_products_gtin
    user = create_user()

    request = factory.get('/products/better-products/{}/?sortBy=ofcomValue'.format(first_product.gtin))
    force_authenticate(request, user=user)
    response = view(request, first_product.gtin)
    response_data = json.loads(response.rendered_content)

    first_product_ofcom_value = response_data['products'][0]['ofcom_value']
    third_product_ofcom_value = response_data['products'][1]['ofcom_value']
    second_product_ofcom_value = response_data['products'][2]['ofcom_value']

    assert response.status_code == 200
    assert len(response_data['products']) == 3
    assert first_product_ofcom_value < third_product_ofcom_value < second_product_ofcom_value
    assert response_data['products'][0]['gtin'] == first_product.gtin
    assert response_data['products'][1]['gtin'] == third_product.gtin
    assert response_data['products'][2]['gtin'] == second_product.gtin


@pytest.mark.django_db
def test_get_better_products_sort_by_health_percentage():

    assert MajorCategory.objects.count() == 0
    assert MinorCategory.objects.count() == 0
    assert Product.objects.count() == 0

    # Major Categories

    maj_cat_16 = mommy.make(MajorCategory, pk=16)

    # Minor Categories

    min_cat_82 = mommy.make(MinorCategory, pk=82, category_major=maj_cat_16)

    # Products
    first_product = mommy.make(Product, gtin=4004980511200, minor_category=min_cat_82,
                               major_category=maj_cat_16, health_percentage=10.0)

    second_product = mommy.make(Product, gtin=29000076501, minor_category=min_cat_82,
                                major_category=maj_cat_16, ofcom_value=1, health_percentage=30.0)

    third_product = mommy.make(Product, gtin=30111187612, minor_category=min_cat_82,
                               major_category=maj_cat_16, health_percentage=20.0)

    assert MajorCategory.objects.count() == 1
    assert MinorCategory.objects.count() == 1
    assert Product.objects.count() == 3

    factory = APIRequestFactory()
    view = get_better_products_gtin
    user = create_user()

    request = factory.get('/products/better-products/{}/?sortBy=healthPercentage'.format(first_product.gtin))
    force_authenticate(request, user=user)
    response = view(request, first_product.gtin)
    response_data = json.loads(response.rendered_content)

    first_product_health_percentage = response_data['products'][0]['health_percentage']
    third_product_health_percentage = response_data['products'][1]['health_percentage']
    second_product_health_percentage = response_data['products'][2]['health_percentage']

    assert response.status_code == 200
    assert len(response_data['products']) == 3
    assert first_product_health_percentage < third_product_health_percentage < second_product_health_percentage
    assert response_data['products'][0]['gtin'] == first_product.gtin
    assert response_data['products'][1]['gtin'] == third_product.gtin
    assert response_data['products'][2]['gtin'] == second_product.gtin


@pytest.mark.django_db
def test_get_better_products_sort_by_protein():

    assert MajorCategory.objects.count() == 0
    assert MinorCategory.objects.count() == 0
    assert Product.objects.count() == 0

    # Major Categories

    maj_cat_16 = mommy.make(MajorCategory, pk=16)

    # Minor Categories

    min_cat_82 = mommy.make(MinorCategory, pk=82, category_major=maj_cat_16)

    # Products

    first_product = mommy.make(Product, gtin=4004980511200, minor_category=min_cat_82,
                               major_category=maj_cat_16)
    test_nutrients = {'name': 'protein', 'amount': 10, 'unit_of_measure': 'g', 'is_mixed': True}
    first_product.nutrients.create(**test_nutrients)
    first_product.save()

    second_product = mommy.make(Product, gtin=29000076501, minor_category=min_cat_82,
                                major_category=maj_cat_16)

    test_nutrients = {'name': 'protein', 'amount': 270, 'unit_of_measure': 'g', 'is_mixed': False}
    second_product.nutrients.create(**test_nutrients)
    second_product.save()

    third_product = mommy.make(Product, gtin=30111187612, minor_category=min_cat_82,
                               major_category=maj_cat_16)

    test_nutrients = {'name': 'protein', 'amount': 50, 'unit_of_measure': 'mg', 'is_mixed': False}
    third_product.nutrients.create(**test_nutrients)
    third_product.save()

    assert MajorCategory.objects.count() == 1
    assert MinorCategory.objects.count() == 1
    assert Product.objects.count() == 3

    factory = APIRequestFactory()
    view = get_better_products_gtin
    user = create_user()

    request = factory.get('/products/better-products/{}/?sortBy=protein'.format(first_product.gtin))
    force_authenticate(request, user=user)
    response = view(request, first_product.gtin)
    response_data = json.loads(response.rendered_content)

    first_product_protein_amount = response_data['products'][0]['nutrients'][0]['amount']
    third_product_protein_amount = response_data['products'][1]['nutrients'][0]['amount']
    second_product_protein_amount = response_data['products'][2]['nutrients'][0]['amount']

    assert response.status_code == 200
    assert len(response_data['products']) == 3
    assert first_product_protein_amount < third_product_protein_amount < second_product_protein_amount
    assert response_data['products'][0]['gtin'] == first_product.gtin
    assert response_data['products'][1]['gtin'] == third_product.gtin
    assert response_data['products'][2]['gtin'] == second_product.gtin


@pytest.mark.django_db
def test_get_better_products_market_regions():

    assert MajorCategory.objects.count() == 0
    assert MinorCategory.objects.count() == 0
    assert Product.objects.count() == 0
    assert MarketRegion.objects.count() == 0

    # Major Categories

    maj_cat_16 = mommy.make(MajorCategory, pk=16)

    # Minor Categories

    min_cat_82 = mommy.make(MinorCategory, pk=82, category_major=maj_cat_16)

    # Products

    first_product = mommy.make(Product, gtin=4004980511200, minor_category=min_cat_82,
                               major_category=maj_cat_16)

    second_product = mommy.make(Product, gtin=29000076501, minor_category=min_cat_82,
                                major_category=maj_cat_16)

    # Market Regions

    mommy.make(MarketRegion, market_region_name='Switzerland', product=first_product)

    mommy.make(MarketRegion, market_region_name='Germany', product=second_product)

    assert MajorCategory.objects.count() == 1
    assert MinorCategory.objects.count() == 1
    assert Product.objects.count() == 2
    assert MarketRegion.objects.count() == 2

    factory = APIRequestFactory()
    view = get_better_products_gtin
    user = create_user()

    request = factory.get('/products/better-products/{}'.format(first_product.gtin))
    force_authenticate(request, user=user)
    response = view(request, first_product.gtin)
    response_data = json.loads(response.rendered_content)

    assert response.status_code == 200
    assert len(response_data['products']) == 2

    request = factory.get('/products/better-products/{}/?marketRegion=ch'.format(first_product.gtin))
    force_authenticate(request, user=user)
    response = view(request, first_product.gtin)
    response_data = json.loads(response.rendered_content)

    assert response.status_code == 200
    assert len(response_data['products']) == 1
    assert response_data['products'][0]['gtin'] == first_product.gtin

    request = factory.get('/products/better-products/{}/?marketRegion=de'.format(first_product.gtin))
    force_authenticate(request, user=user)
    response = view(request, first_product.gtin)
    response_data = json.loads(response.rendered_content)

    assert response.status_code == 200
    assert len(response_data['products']) == 1
    assert response_data['products'][0]['gtin'] == second_product.gtin

    request = factory.get('/products/better-products/{}/?marketRegion=xyz'.format(first_product.gtin))
    force_authenticate(request, user=user)
    response = view(request, first_product.gtin)
    response_data = json.loads(response.rendered_content)

    assert response.status_code == 200
    assert not response_data['success']


@pytest.mark.django_db
def test_get_better_products_retailers():

    assert MajorCategory.objects.count() == 0
    assert MinorCategory.objects.count() == 0
    assert Product.objects.count() == 0
    assert Retailer.objects.count() == 0

    # Major Categories

    maj_cat_16 = mommy.make(MajorCategory, pk=16)

    # Minor Categories

    min_cat_82 = mommy.make(MinorCategory, pk=82, category_major=maj_cat_16)

    # Products

    first_product = mommy.make(Product, gtin=4004980511200, minor_category=min_cat_82,
                               major_category=maj_cat_16)

    second_product = mommy.make(Product, gtin=29000076501, minor_category=min_cat_82,
                                major_category=maj_cat_16)

    # Retailers

    mommy.make(Retailer, retailer_name='Migros', product=first_product)

    mommy.make(Retailer, retailer_name='Edeka', product=second_product)

    assert MajorCategory.objects.count() == 1
    assert MinorCategory.objects.count() == 1
    assert Product.objects.count() == 2
    assert Retailer.objects.count() == 2

    factory = APIRequestFactory()
    view = get_better_products_gtin
    user = create_user()

    request = factory.get('/products/better-products/{}'.format(first_product.gtin))
    force_authenticate(request, user=user)
    response = view(request, first_product.gtin)
    response_data = json.loads(response.rendered_content)

    assert response.status_code == 200
    assert len(response_data['products']) == 2

    request = factory.get('/products/better-products/{}/?retailer=Migros'.format(first_product.gtin))
    force_authenticate(request, user=user)
    response = view(request, first_product.gtin)
    response_data = json.loads(response.rendered_content)

    assert response.status_code == 200
    assert len(response_data['products']) == 1

    request = factory.get('/products/better-products/{}/?retailer=edEka'.format(first_product.gtin))
    force_authenticate(request, user=user)
    response = view(request, first_product.gtin)
    response_data = json.loads(response.rendered_content)

    assert response.status_code == 200
    assert len(response_data['products']) == 1

    request = factory.get('/products/better-products/{}/?retailer=xyz'.format(first_product.gtin))
    force_authenticate(request, user=user)
    response = view(request, first_product.gtin)
    response_data = json.loads(response.rendered_content)

    assert response.status_code == 200
    assert not response_data['success']
