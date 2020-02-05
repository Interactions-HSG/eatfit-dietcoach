import pytest
from model_mommy import mommy

from django.contrib.auth.models import User

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.reverse import reverse
from rest_framework import status

from NutritionService.views import views
from NutritionService import models
from basket_analysis_data import BASKET_ANALYSIS_DATA


@pytest.mark.django_db
def test_basket_analysis_api_is_valid():
    """
    Assert that the API request is valid (less than 10 receipts and correct data is provided).
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

    user = User.objects.create_user(username='test', password='test')
    r2n_partner = mommy.make(models.ReceiptToNutritionPartner, user=user, name='Kevin')
    r2n_user = mommy.make(models.ReceiptToNutritionUser, r2n_partner=r2n_partner, r2n_username='Kevin')

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

    BASKET_ANALYSIS_DATA['r2n_partner'] = r2n_partner.name
    BASKET_ANALYSIS_DATA['r2n_username'] = r2n_user.r2n_username

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
    request = api_client.post(url, BASKET_ANALYSIS_DATA, format='json')
    force_authenticate(request, user=user)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert models.NonFoundMatching.objects.count() == 0
    assert models.DigitalReceipt.objects.count() == 5
