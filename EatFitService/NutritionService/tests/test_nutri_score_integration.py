from model_mommy import mommy
import pytest

from NutritionService.models import BEVERAGE, MINERAL_WATER, MinorCategory, MajorCategory, NutriScoreFacts, \
    NutritionFact, Product


@pytest.mark.django_db
def test_nutri_score_main_beverage():
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

    mommy.make(NutritionFact, product=test_product, name='energyKJ', amount=28.2, unit_of_measure='kj', is_mixed=True)
    mommy.make(NutritionFact, product=test_product, name='saturatedFat', amount=0.53, unit_of_measure='g', is_mixed=True)
    mommy.make(NutritionFact, product=test_product, name='sugars', amount=1.16, unit_of_measure='g', is_mixed=True)
    mommy.make(NutritionFact, product=test_product, name='dietaryFiber', amount=0.21, unit_of_measure='g', is_mixed=True)
    mommy.make(NutritionFact, product=test_product, name='protein', amount=0.74, unit_of_measure='g', is_mixed=True)
    mommy.make(NutritionFact, product=test_product, name='sodium', amount=62, unit_of_measure='mg', is_mixed=True)

    assert MajorCategory.objects.count() == 1
    assert MinorCategory.objects.count() == 1
    assert NutritionFact.objects.count() == 12
    assert Product.objects.count() == 1

    test_product.save()

    assert test_product.nutri_score_number_of_errors == 0
    assert test_product.ofcom_value == 27
    assert test_product.nutri_score_calculated == 'E'
    assert test_product.nutri_score_calculated_mixed == 'C'
    assert test_product.nutri_score_final == 'C'

    test_product_ns_facts = NutriScoreFacts.objects.get(product=test_product)

    assert test_product_ns_facts.fvpn_total_percentage == 15
    assert test_product_ns_facts.ofcom_n_energy_kj == 10.0
    assert test_product_ns_facts.ofcom_n_energy_kj_mixed == 1.0
    assert test_product_ns_facts.ofcom_n_saturated_fat == 5.0
    assert test_product_ns_facts.ofcom_n_saturated_fat_mixed == 0.0
    assert test_product_ns_facts.ofcom_n_sugars == 8.0
    assert test_product_ns_facts.ofcom_n_sugars_mixed == 1.0
    assert test_product_ns_facts.ofcom_n_salt == 6.0
    assert test_product_ns_facts.ofcom_n_salt_mixed == 0.0
    assert test_product_ns_facts.ofcom_p_dietary_fiber == 2.0
    assert test_product_ns_facts.ofcom_p_dietary_fiber_mixed == 0.0
    assert test_product_ns_facts.ofcom_p_fvpn == 0.0
    assert test_product_ns_facts.ofcom_p_fvpn_mixed == 0.0
    assert test_product_ns_facts.ofcom_p_protein == 4.0
    assert test_product_ns_facts.ofcom_p_protein_mixed == 0.0

@pytest.mark.django_db
def test_nutri_score_manufacturer_final():
    """
    Test Case:
    1) Manufacturer nutri score takes precedence over both mixed and calculated nutri score values
    """
    assert MajorCategory.objects.count() == 0
    assert MinorCategory.objects.count() == 0
    assert Product.objects.count() == 0

    major_category = mommy.make(MajorCategory, pk=16)
    minor_category = mommy.make(MinorCategory, pk=82, category_major=major_category, nutri_score_category=MINERAL_WATER)
    test_product = mommy.make(Product, minor_category=minor_category, health_percentage=15,
                              nutri_score_by_manufacturer='C', nutri_score_calculated_mixed='B')

    assert MajorCategory.objects.count() == 1
    assert MinorCategory.objects.count() == 1
    assert Product.objects.count() == 1

    test_product.save()

    assert test_product.nutri_score_number_of_errors == 0
    assert test_product.ofcom_value == -15
    assert test_product.nutri_score_calculated == 'A'
    assert test_product.nutri_score_final == 'C'
