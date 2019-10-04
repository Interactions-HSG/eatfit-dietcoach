from model_mommy import mommy
import pytest

from NutritionService.models import BEVERAGE, MinorCategory, MajorCategory, NutriScoreFacts, NutritionFact, Product


@pytest.mark.django_db
def test_nutriscore_main_beverage():
    assert MajorCategory.objects.count() == 0
    assert MinorCategory.objects.count() == 0
    assert NutriScoreFacts.objects.count() == 0
    assert NutritionFact.objects.count() == 0
    assert Product.objects.count() == 0

    major_category = mommy.make(MajorCategory, pk=16)
    minor_category = mommy.make(MinorCategory, pk=82, category_major=major_category, nutri_score_category=BEVERAGE)
    test_product = mommy.make(Product, minor_category=minor_category, health_percentage=15)
    mommy.make(NutritionFact, product=test_product, name='energyKJ', amount=280.2, unit_of_measure='kj')
    mommy.make(NutritionFact, product=test_product, name='saturatedFat', amount=5.3, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='sugars', amount=11.6, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='dietaryFiber', amount=2.1, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='protein', amount=7.4, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='sodium', amount=620, unit_of_measure='mg')

    mommy.make(NutritionFact, product=test_product, name='energyKJ', amount=280.2, unit_of_measure='kj', is_mixed=True)
    mommy.make(NutritionFact, product=test_product, name='saturatedFat', amount=5.3, unit_of_measure='g', is_mixed=True)
    mommy.make(NutritionFact, product=test_product, name='sugars', amount=11.6, unit_of_measure='g', is_mixed=True)
    mommy.make(NutritionFact, product=test_product, name='dietaryFiber', amount=2.1, unit_of_measure='g', is_mixed=True)
    mommy.make(NutritionFact, product=test_product, name='protein', amount=7.4, unit_of_measure='g', is_mixed=True)
    mommy.make(NutritionFact, product=test_product, name='sodium', amount=620, unit_of_measure='mg', is_mixed=True)

    assert MajorCategory.objects.count() == 1
    assert MinorCategory.objects.count() == 1
    assert NutritionFact.objects.count() == 12
    assert Product.objects.count() == 1

    test_product.save()

    assert test_product.nutri_score_number_of_errors == 0
    assert test_product.ofcom_value == 27
    assert test_product.nutri_score_calculated == 'E'
    assert test_product.nutri_score_calculated_mixed == 'E'

    test_product_ns_facts = NutriScoreFacts.objects.get(product=test_product)

    assert test_product_ns_facts.fvpn_total_percentage == 15
    assert test_product_ns_facts.ofcom_n_energy_kj == 10.0
    assert test_product_ns_facts.ofcom_n_energy_kj_mixed == 10.0
    assert test_product_ns_facts.ofcom_n_saturated_fat == 5.0
    assert test_product_ns_facts.ofcom_n_saturated_fat_mixed == 5.0
    assert test_product_ns_facts.ofcom_n_sugars == 8.0
    assert test_product_ns_facts.ofcom_n_sugars_mixed == 8.0
    assert test_product_ns_facts.ofcom_n_salt == 6.0
    assert test_product_ns_facts.ofcom_n_salt_mixed == 6.0
    assert test_product_ns_facts.ofcom_p_dietary_fiber == 2.0
    assert test_product_ns_facts.ofcom_p_dietary_fiber_mixed == 2.0
    assert test_product_ns_facts.ofcom_p_fvpn == 0.0
    assert test_product_ns_facts.ofcom_p_fvpn_mixed == 0.0
    assert test_product_ns_facts.ofcom_p_protein == 4.0
    assert test_product_ns_facts.ofcom_p_protein_mixed == 4.0
