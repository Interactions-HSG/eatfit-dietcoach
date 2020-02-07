import pytest
from model_mommy import mommy

from django.contrib.auth.models import User

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.reverse import reverse
from rest_framework import status

from NutritionService import models
from NutritionService.views import views
from NutritionService.views.errors import BasketAnalysisErrors
from basket_analysis_data import BASKET_ANALYSIS_DATA_SIMPLE, BASKET_ANALYSIS_DATA_DETAILED

TEST_USER_AND_PASSWORD = 'test'
PARTNER_AND_USER_NAME = 'Karen'
URL_REVERSE = 'basket-analysis'
ERROR_KEY = 'error'
ARTICLE_ID_SIMPLE = 'Apfel Braeburn'
ARTICLE_TYPE_SIMPLE = 'Migros_long_v1'

errors = BasketAnalysisErrors()


@pytest.mark.django_db
def test_basket_analysis_api_forbidden_request():
    """
    Assert that a request without partner data does not get processed.
    """
    assert User.objects.count() == 0
    assert models.ReceiptToNutritionPartner.objects.count() == 0

    user = User.objects.create_user(username=TEST_USER_AND_PASSWORD, password=TEST_USER_AND_PASSWORD)

    assert User.objects.count() == 1

    BASKET_ANALYSIS_DATA_SIMPLE['r2n_partner'] = ''
    BASKET_ANALYSIS_DATA_SIMPLE['r2n_username'] = ''

    api_client = APIRequestFactory()
    view = views.BasketAnalysisView.as_view()
    url = reverse(URL_REVERSE)
    request = api_client.post(url, BASKET_ANALYSIS_DATA_SIMPLE, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert ERROR_KEY in response.data
    assert response.data[ERROR_KEY] == errors.PARTNER_DOES_NOT_EXIST


@pytest.mark.django_db
def test_basket_analysis_api_serializer_invalid():
    """
    Assert that invalid request data does not get processed.
    """
    assert User.objects.count() == 0
    assert models.ReceiptToNutritionPartner.objects.count() == 0

    user = User.objects.create_user(username=TEST_USER_AND_PASSWORD, password=TEST_USER_AND_PASSWORD)
    mommy.make(models.ReceiptToNutritionPartner, user=user)

    assert User.objects.count() == 1
    assert models.ReceiptToNutritionPartner.objects.count() == 1

    BASKET_ANALYSIS_DATA_SIMPLE['r2n_partner'] = ''
    BASKET_ANALYSIS_DATA_SIMPLE['r2n_username'] = ''

    api_client = APIRequestFactory()
    view = views.BasketAnalysisView.as_view()
    url = reverse(URL_REVERSE)
    request = api_client.post(url, BASKET_ANALYSIS_DATA_SIMPLE, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_basket_analysis_api_user_partner_does_not_exist():
    """
    Assert that a request of a non-existant partner does not get processed.
    """
    assert User.objects.count() == 0
    assert models.ReceiptToNutritionPartner.objects.count() == 0
    assert models.ReceiptToNutritionUser.objects.count() == 0

    user = User.objects.create_user(username=TEST_USER_AND_PASSWORD, password=TEST_USER_AND_PASSWORD)
    mommy.make(models.ReceiptToNutritionPartner, user=user)

    BASKET_ANALYSIS_DATA_SIMPLE['r2n_partner'] = PARTNER_AND_USER_NAME
    BASKET_ANALYSIS_DATA_SIMPLE['r2n_username'] = PARTNER_AND_USER_NAME

    assert User.objects.count() == 1
    assert models.ReceiptToNutritionPartner.objects.count() == 1
    assert models.ReceiptToNutritionUser.objects.count() == 0

    api_client = APIRequestFactory()
    view = views.BasketAnalysisView.as_view()
    url = reverse(URL_REVERSE)
    request = api_client.post(url, BASKET_ANALYSIS_DATA_SIMPLE, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_basket_analysis_api_user_partner_is_inactive():
    """
    Assert that a request of an inactive partner does not get processed.
    """
    assert User.objects.count() == 0
    assert models.ReceiptToNutritionPartner.objects.count() == 0
    assert models.ReceiptToNutritionUser.objects.count() == 0

    user = User.objects.create_user(username=TEST_USER_AND_PASSWORD, password=TEST_USER_AND_PASSWORD)
    r2n_partner = mommy.make(models.ReceiptToNutritionPartner, user=user, name=PARTNER_AND_USER_NAME)
    r2n_user = mommy.make(models.ReceiptToNutritionUser, r2n_partner=r2n_partner, r2n_username=PARTNER_AND_USER_NAME,
                          r2n_user_active=False)

    BASKET_ANALYSIS_DATA_SIMPLE['r2n_partner'] = r2n_partner.name
    BASKET_ANALYSIS_DATA_SIMPLE['r2n_username'] = r2n_user.r2n_username

    assert User.objects.count() == 1
    assert models.ReceiptToNutritionPartner.objects.count() == 1
    assert models.ReceiptToNutritionUser.objects.count() == 1

    api_client = APIRequestFactory()
    view = views.BasketAnalysisView.as_view()
    url = reverse(URL_REVERSE)
    request = api_client.post(url, BASKET_ANALYSIS_DATA_SIMPLE, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert ERROR_KEY in response.data
    assert response.data[ERROR_KEY] == errors.USER_INACTIVE


@pytest.mark.django_db
def test_basket_analysis_api_non_found_does_not_exist():
    """
    Assert that when no matching was found and a NonFoundMatching object does not exist that it gets created.
    """
    assert User.objects.count() == 0
    assert models.ReceiptToNutritionPartner.objects.count() == 0
    assert models.ReceiptToNutritionUser.objects.count() == 0
    assert models.Matching.objects.count() == 0
    assert models.NonFoundMatching.objects.count() == 0

    user = User.objects.create_user(username=TEST_USER_AND_PASSWORD, password=TEST_USER_AND_PASSWORD)
    r2n_partner = mommy.make(models.ReceiptToNutritionPartner, user=user, name=PARTNER_AND_USER_NAME)
    r2n_user = mommy.make(models.ReceiptToNutritionUser, r2n_partner=r2n_partner, r2n_username=PARTNER_AND_USER_NAME)

    BASKET_ANALYSIS_DATA_SIMPLE['r2n_partner'] = r2n_partner.name
    BASKET_ANALYSIS_DATA_SIMPLE['r2n_username'] = r2n_user.r2n_username

    assert User.objects.count() == 1
    assert models.ReceiptToNutritionPartner.objects.count() == 1
    assert models.ReceiptToNutritionUser.objects.count() == 1

    api_client = APIRequestFactory()
    view = views.SendReceiptsView.as_view()
    url = reverse(URL_REVERSE)
    request = api_client.post(url, BASKET_ANALYSIS_DATA_SIMPLE, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert models.ReceiptToNutritionUser.objects.count() == 1
    assert models.NonFoundMatching.objects.count() == 1


@pytest.mark.django_db
def test_basket_analysis_api_matching_non_found_exists():
    """
    Assert that when no matching was found and a NonFoundMatching object exists that its counter is incremented.
    """
    assert User.objects.count() == 0
    assert models.ReceiptToNutritionPartner.objects.count() == 0
    assert models.ReceiptToNutritionUser.objects.count() == 0
    assert models.Matching.objects.count() == 0
    assert models.NonFoundMatching.objects.count() == 0

    user = User.objects.create_user(username=TEST_USER_AND_PASSWORD, password=TEST_USER_AND_PASSWORD)
    r2n_partner = mommy.make(models.ReceiptToNutritionPartner, user=user, name=PARTNER_AND_USER_NAME)
    r2n_user = mommy.make(models.ReceiptToNutritionUser, r2n_partner=r2n_partner, r2n_username=PARTNER_AND_USER_NAME)
    mommy.make(models.NonFoundMatching, article_id=ARTICLE_ID_SIMPLE, article_type=ARTICLE_TYPE_SIMPLE, counter=0)

    BASKET_ANALYSIS_DATA_SIMPLE['r2n_partner'] = r2n_partner.name
    BASKET_ANALYSIS_DATA_SIMPLE['r2n_username'] = r2n_user.r2n_username

    assert User.objects.count() == 1
    assert models.ReceiptToNutritionPartner.objects.count() == 1
    assert models.ReceiptToNutritionUser.objects.count() == 1
    assert models.NonFoundMatching.objects.count() == 1

    api_client = APIRequestFactory()
    view = views.SendReceiptsView.as_view()
    url = reverse(URL_REVERSE)
    request = api_client.post(url, BASKET_ANALYSIS_DATA_SIMPLE, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert models.NonFoundMatching.objects.count() == 1

    test_object = models.NonFoundMatching.objects.get(article_id=ARTICLE_ID_SIMPLE, article_type='Migros_long_v1')

    assert test_object.counter == 1


@pytest.mark.django_db
def test_basket_analysis_api_matching_multiple():
    """
    Assert that when multiple identical matchings occur that the first one is selected.
    """
    assert User.objects.count() == 0
    assert models.ReceiptToNutritionPartner.objects.count() == 0
    assert models.ReceiptToNutritionUser.objects.count() == 0
    assert models.Matching.objects.count() == 0
    assert models.NonFoundMatching.objects.count() == 0
    assert models.Product.objects.count() == 0

    user = User.objects.create_user(username=TEST_USER_AND_PASSWORD, password=TEST_USER_AND_PASSWORD)
    r2n_partner = mommy.make(models.ReceiptToNutritionPartner, user=user, name=PARTNER_AND_USER_NAME)
    r2n_user = mommy.make(models.ReceiptToNutritionUser, r2n_partner=r2n_partner, r2n_username=PARTNER_AND_USER_NAME)
    test_product = mommy.make(models.Product)
    mommy.make(models.Matching, article_id=ARTICLE_ID_SIMPLE, article_type=ARTICLE_TYPE_SIMPLE, gtin=0,
               eatfit_product=test_product)
    mommy.make(models.Matching, article_id=ARTICLE_ID_SIMPLE, article_type=ARTICLE_TYPE_SIMPLE, gtin=1,
               eatfit_product=test_product)

    BASKET_ANALYSIS_DATA_SIMPLE['r2n_partner'] = r2n_partner.name
    BASKET_ANALYSIS_DATA_SIMPLE['r2n_username'] = r2n_user.r2n_username

    assert User.objects.count() == 1
    assert models.ReceiptToNutritionPartner.objects.count() == 1
    assert models.ReceiptToNutritionUser.objects.count() == 1
    assert models.Matching.objects.count() == 2
    assert models.Product.objects.count() == 1

    api_client = APIRequestFactory()
    view = views.SendReceiptsView.as_view()
    url = reverse(URL_REVERSE)
    request = api_client.post(url, BASKET_ANALYSIS_DATA_SIMPLE, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert models.NonFoundMatching.objects.count() == 0

    test_object = models.Matching.objects.filter().first()

    assert test_object.gtin == 0


@pytest.mark.django_db
def test_basket_analysis_api_matching_valid():
    """
    Assert that product is matched correctly and valid.
    """
    assert User.objects.count() == 0
    assert models.ReceiptToNutritionPartner.objects.count() == 0
    assert models.ReceiptToNutritionUser.objects.count() == 0
    assert models.Matching.objects.count() == 0
    assert models.NonFoundMatching.objects.count() == 0
    assert models.Product.objects.count() == 0

    user = User.objects.create_user(username=TEST_USER_AND_PASSWORD, password=TEST_USER_AND_PASSWORD)
    r2n_partner = mommy.make(models.ReceiptToNutritionPartner, user=user, name=PARTNER_AND_USER_NAME)
    r2n_user = mommy.make(models.ReceiptToNutritionUser, r2n_partner=r2n_partner, r2n_username=PARTNER_AND_USER_NAME)
    test_product = mommy.make(models.Product)
    mommy.make(models.Matching, article_id=ARTICLE_ID_SIMPLE, article_type=ARTICLE_TYPE_SIMPLE,
               eatfit_product=test_product)

    BASKET_ANALYSIS_DATA_SIMPLE['r2n_partner'] = r2n_partner.name
    BASKET_ANALYSIS_DATA_SIMPLE['r2n_username'] = r2n_user.r2n_username

    assert User.objects.count() == 1
    assert models.ReceiptToNutritionPartner.objects.count() == 1
    assert models.ReceiptToNutritionUser.objects.count() == 1
    assert models.Matching.objects.count() == 1
    assert models.Product.objects.count() == 1

    api_client = APIRequestFactory()
    view = views.SendReceiptsView.as_view()
    url = reverse(URL_REVERSE)
    request = api_client.post(url, BASKET_ANALYSIS_DATA_SIMPLE, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert models.NonFoundMatching.objects.count() == 0


@pytest.mark.django_db
def test_basket_analysis_api_is_valid():
    """
    Assert that the API request and calculations are valid (full integration).
    """
    assert User.objects.count() == 0
    assert models.ReceiptToNutritionPartner.objects.count() == 0
    assert models.ReceiptToNutritionUser.objects.count() == 0
    assert models.MajorCategory.objects.count() == 0
    assert models.MinorCategory.objects.count() == 0
    assert models.Product.objects.count() == 0
    assert models.NutritionFact.objects.count() == 0
    assert models.Matching.objects.count() == 0
    assert models.NonFoundMatching.objects.count() == 0
    assert models.DigitalReceipt.objects.count() == 0

    user = User.objects.create_user(username=TEST_USER_AND_PASSWORD, password=TEST_USER_AND_PASSWORD)
    r2n_partner = mommy.make(models.ReceiptToNutritionPartner, user=user, name=PARTNER_AND_USER_NAME)
    r2n_user = mommy.make(models.ReceiptToNutritionUser, r2n_partner=r2n_partner, r2n_username=PARTNER_AND_USER_NAME)

    major_category = mommy.make(models.MajorCategory, pk=16)
    first_minor_category = mommy.make(models.MinorCategory, pk=82, category_major=major_category,
                                      nutri_score_category=models.FOOD)
    second_minor_category = mommy.make(models.MinorCategory, pk=83, category_major=major_category,
                                       nutri_score_category=models.FOOD)
    third_minor_category = mommy.make(models.MinorCategory, pk=84, category_major=major_category,
                                      nutri_score_category=models.FOOD)
    fourth_minor_category = mommy.make(models.MinorCategory, pk=85, category_major=major_category,
                                       nutri_score_category=models.FOOD)
    fifth_minor_category = mommy.make(models.MinorCategory, pk=86, category_major=major_category,
                                      nutri_score_category=models.FOOD)

    first_product = mommy.make(models.Product, gtin=1, product_name_de='DV extra fin Chia & Quinoa 4PP 184g',
                               major_category=major_category, minor_category=first_minor_category, health_percentage=1,
                               product_size_unit_of_measure='kg', product_size='1.729')
    mommy.make(models.Matching, eatfit_product=first_product, article_id='DV extra fin Chia & Quinoa 4PP 184g',
               article_type='Migros_long_v1', gtin=1)
    mommy.make(models.NutritionFact, product=first_product, name='totalFat', amount=16.0, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=first_product, name='saturatedFat', amount=1.8, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=first_product, name='totalCarbohydrate', amount=54.0, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=first_product, name='sugars', amount=1.9, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=first_product, name='dietaryFiber', amount=10.0, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=first_product, name='protein', amount=14.0, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=first_product, name='salt', amount=1.9, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=first_product, name='sodium', amount=0.82, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=first_product, name='energyKJ', amount=1830.0, unit_of_measure='KJ')
    mommy.make(models.NutritionFact, product=first_product, name='energyKcal', amount=436.0, unit_of_measure='Kcal')
    mommy.make(models.NutritionFact, product=first_product, name='availableCarbohydrate', amount=54.0,
               unit_of_measure='g')
    first_product.save()

    assert first_product.data_score >= 25
    assert first_product.nutri_score_final is not None

    second_product = mommy.make(models.Product, gtin=2, product_name_de='Dessert-Tart. Royal 5cm 8 x 23 St.',
                                major_category=major_category, minor_category=second_minor_category,
                                health_percentage=1,
                                product_size_unit_of_measure='kg', product_size='0.184')
    mommy.make(models.Matching, eatfit_product=second_product, article_id='Dessert-Tart. Royal 5cm 8 x 23 St.',
               article_type='Migros_long_v1', gtin=2)
    mommy.make(models.NutritionFact, product=second_product, name='totalFat', amount=25.0, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=second_product, name='saturatedFat', amount=12.0, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=second_product, name='totalCarbohydrate', amount=65.0, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=second_product, name='sugars', amount=21.0, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=second_product, name='dietaryFiber', amount=2.5, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=second_product, name='protein', amount=6.2, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=second_product, name='salt', amount=0.12, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=second_product, name='sodium', amount=0.05, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=second_product, name='energyKJ', amount=2162.0, unit_of_measure='KJ')
    mommy.make(models.NutritionFact, product=second_product, name='energyKcal', amount=516.0, unit_of_measure='Kcal')
    mommy.make(models.NutritionFact, product=second_product, name='availableCarbohydrate', amount=65.0,
               unit_of_measure='g')
    second_product.save()

    assert second_product.data_score >= 25
    assert second_product.nutri_score_final is not None

    third_product = mommy.make(models.Product, gtin=3, product_name_de='Mini Hüppen 1kg ca. 650 Stück',
                               major_category=major_category, minor_category=third_minor_category, health_percentage=1,
                               product_size_unit_of_measure='kg', product_size='1')
    mommy.make(models.Matching, eatfit_product=third_product, article_id='Mini Hüppen 1kg ca. 650 Stück',
               article_type='Migros_long_v1', gtin=3)
    mommy.make(models.NutritionFact, product=third_product, name='totalFat', amount=9.1, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=third_product, name='saturatedFat', amount=4.6, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=third_product, name='totalCarbohydrate', amount=80.0, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=third_product, name='sugars', amount=31.0, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=third_product, name='dietaryFiber', amount=2.9, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=third_product, name='protein', amount=8.4, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=third_product, name='salt', amount=0.68, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=third_product, name='sodium', amount=0.21, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=third_product, name='energyKJ', amount=1818.0, unit_of_measure='KJ')
    mommy.make(models.NutritionFact, product=third_product, name='energyKcal', amount=431.0, unit_of_measure='Kcal')
    mommy.make(models.NutritionFact, product=third_product, name='availableCarbohydrate', amount=77.0,
               unit_of_measure='g')
    third_product.save()

    assert third_product.data_score >= 25
    assert third_product.nutri_score_final is not None

    fourth_product = mommy.make(models.Product, gtin=4, product_name_de='Alnatura Black Bean Cashew Burger',
                                major_category=major_category, minor_category=fourth_minor_category,
                                health_percentage=1,
                                product_size_unit_of_measure='g', product_size='160')
    mommy.make(models.Matching, eatfit_product=fourth_product, article_id='Alnatura Black Bean Cashew Burger',
               article_type='Migros_long_v1', gtin=4)
    mommy.make(models.NutritionFact, product=fourth_product, name='totalFat', amount=13.0, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=fourth_product, name='saturatedFat', amount=4.6, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=fourth_product, name='totalCarbohydrate', amount=20.0, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=fourth_product, name='sugars', amount=2.6, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=fourth_product, name='dietaryFiber', amount=8.7, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=fourth_product, name='protein', amount=5.9, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=fourth_product, name='salt', amount=1.2, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=fourth_product, name='sodium', amount=0.02, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=fourth_product, name='energyKJ', amount=991.0, unit_of_measure='KJ')
    mommy.make(models.NutritionFact, product=fourth_product, name='energyKcal', amount=238.0, unit_of_measure='Kcal')
    fourth_product.save()

    assert fourth_product.data_score >= 25
    assert fourth_product.nutri_score_final is not None

    fifth_product = mommy.make(models.Product, gtin=5, product_name_de='Rindshackfleisch 500g',
                               major_category=major_category, minor_category=fifth_minor_category, health_percentage=1,
                               product_size_unit_of_measure='g', product_size='500')
    mommy.make(models.Matching, eatfit_product=fifth_product, article_id='Rindshackfleisch 500g',
               article_type='Migros_long_v1', gtin=5)
    mommy.make(models.NutritionFact, product=fifth_product, name='totalFat', amount=12.0, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=fifth_product, name='saturatedFat', amount=4.6, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=fifth_product, name='totalCarbohydrate', amount=1.0, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=fifth_product, name='sugars', amount=2.6, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=fifth_product, name='dietaryFiber', amount=8.7, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=fifth_product, name='protein', amount=19.0, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=fifth_product, name='salt', amount=0.1, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=fifth_product, name='sodium', amount=0.04, unit_of_measure='g')
    mommy.make(models.NutritionFact, product=fifth_product, name='energyKJ', amount=780.0, unit_of_measure='KJ')
    mommy.make(models.NutritionFact, product=fifth_product, name='energyKcal', amount=186.0, unit_of_measure='Kcal')
    fifth_product.save()

    assert fifth_product.data_score >= 25
    assert fifth_product.nutri_score_final is not None

    BASKET_ANALYSIS_DATA_DETAILED['r2n_partner'] = r2n_partner.name
    BASKET_ANALYSIS_DATA_DETAILED['r2n_username'] = r2n_user.r2n_username

    assert User.objects.count() == 1
    assert models.ReceiptToNutritionPartner.objects.count() == 1
    assert models.ReceiptToNutritionUser.objects.count() == 1
    assert models.MajorCategory.objects.count() == 1
    assert models.MinorCategory.objects.count() == 5
    assert models.Product.objects.count() == 5
    assert models.Matching.objects.count() == 5
    assert models.NutritionFact.objects.count() == 53

    api_client = APIRequestFactory()
    view = views.BasketAnalysisView.as_view()
    url = reverse('basket-analysis')
    request = api_client.post(url, BASKET_ANALYSIS_DATA_DETAILED, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    expected_results = {'nutri_score_by_basket': [
        {'receipt_id': '1551533421', 'receipt_datetime': '2019-03-02T14:30:21Z',
         'business_unit': 'Migros', 'nutri_score_average': 'C', 'nutri_score_indexed': 2.96}], 'nutri_score_by_week': [
        {'name_calendar_week': '2019-08', 'nutri_score_average': 'C', 'nutri_score_indexed': 2.96,
         'start_date': '2019-02-25T00:00:00Z', 'end_date': '2019-03-03T00:00:00Z'}], 'improvement_potential': [
        {'nutrient': 'saturatedFat', 'ofcom_point_average': 4.6, 'potential_percentage': 20.19, 'amount': 129.56,
         'unit': 'g', 'sources': [{'minor_category_id': 84, 'amount': 46.0, 'unit': 'g'},
                                  {'minor_category_id': 82, 'amount': 31.12, 'unit': 'g'},
                                  {'minor_category_id': 86, 'amount': 23.0, 'unit': 'g'},
                                  {'minor_category_id': 83, 'amount': 22.08, 'unit': 'g'},
                                  {'minor_category_id': 85, 'amount': 7.36, 'unit': 'g'}]},
        {'nutrient': 'sugars', 'ofcom_point_average': 2.0, 'potential_percentage': 13.32, 'amount': 398.65, 'unit': 'g',
         'sources': [{'minor_category_id': 84, 'amount': 310.0, 'unit': 'g'},
                     {'minor_category_id': 83, 'amount': 38.64, 'unit': 'g'},
                     {'minor_category_id': 82, 'amount': 32.85, 'unit': 'g'},
                     {'minor_category_id': 86, 'amount': 13.0, 'unit': 'g'},
                     {'minor_category_id': 85, 'amount': 4.16, 'unit': 'g'}]},
        {'nutrient': 'salt', 'ofcom_point_average': 2.2, 'potential_percentage': 34.72, 'amount': 42.29, 'unit': 'g',
         'sources': [{'minor_category_id': 82, 'amount': 32.85, 'unit': 'g'},
                     {'minor_category_id': 84, 'amount': 6.8, 'unit': 'g'},
                     {'minor_category_id': 85, 'amount': 1.92, 'unit': 'g'},
                     {'minor_category_id': 86, 'amount': 0.5, 'unit': 'g'},
                     {'minor_category_id': 83, 'amount': 0.22, 'unit': 'g'}]},
        {'nutrient': 'energyKcal', 'ofcom_point_average': 4.0, 'potential_percentage': 31.77, 'amount': 14108.68,
         'unit': 'kcal', 'sources': [{'minor_category_id': 82, 'amount': 7538.44, 'unit': 'kcal'},
                                     {'minor_category_id': 84, 'amount': 4310.0, 'unit': 'kcal'},
                                     {'minor_category_id': 83, 'amount': 949.44, 'unit': 'kcal'},
                                     {'minor_category_id': 86, 'amount': 930.0, 'unit': 'kcal'},
                                     {'minor_category_id': 85, 'amount': 380.8, 'unit': 'kcal'}]}]}

    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected_results
    assert models.NonFoundMatching.objects.count() == 0
    assert models.DigitalReceipt.objects.count() == 5
