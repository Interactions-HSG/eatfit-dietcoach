from model_mommy import mommy
import pytest

from NutritionService.models import BEVERAGE, Product, NutriScoreFacts, determine_fvpn_share
from NutritionService.nutriscore.calculations import calculate_fvpn_percentage


def test_fvpn_percentage_calculation():
    fruit_percentage = 12
    fruit_percentage_dried = 4
    vegetable_percentage = 19
    vegetable_percentage_dried = 2
    pulses_percentage = 15
    pulses_percentage_dried = 10
    nuts_percentage = 8

    result = calculate_fvpn_percentage(fruit_percentage, fruit_percentage_dried, vegetable_percentage,
                                       vegetable_percentage_dried, pulses_percentage, pulses_percentage_dried,
                                       nuts_percentage)

    assert result <= 100
    assert result > 74

    fruit_percentage = 100
    fruit_percentage_dried = 100
    vegetable_percentage = 100
    vegetable_percentage_dried = 100
    pulses_percentage = 100
    pulses_percentage_dried = 100
    nuts_percentage = 100

    result = calculate_fvpn_percentage(fruit_percentage, fruit_percentage_dried, vegetable_percentage,
                                       vegetable_percentage_dried, pulses_percentage, pulses_percentage_dried,
                                       nuts_percentage)

    assert result <= 100


@pytest.mark.django_db
def test_determine_fvpn_share():
    """
    Test Cases:
    1) mixed = True
    2) NutriScoreFacts does not exist and Product has no health percentage field
    3) NutriScoreFacts does not exist and Product has a health percentage field
    4) NutriScoreFacts exists and has missing fields
    5) NutriScoreFacts exists and has all fields
    """
    assert Product.objects.count() == 0
    assert NutriScoreFacts.objects.count() == 0

    first_test_product = mommy.make(Product)

    assert Product.objects.count() == 1

    category = BEVERAGE
    first_result = determine_fvpn_share(first_test_product, category, mixed=True)

    assert 'ofcom_p_fvpn' not in first_result
    assert 'ofcom_p_fvpn_mixed' in first_result
    assert first_result['ofcom_p_fvpn_mixed'] == 0
    assert 'fvpn_total_percentage_estimated' in first_result
    assert first_result['fvpn_total_percentage_estimated'] == 0

    second_result = determine_fvpn_share(first_test_product, category)

    assert 'ofcom_p_fvpn_mixed' not in second_result
    assert 'ofcom_p_fvpn' in second_result
    assert second_result['ofcom_p_fvpn'] == 0
    assert 'fvpn_total_percentage_estimated' in second_result
    assert second_result['fvpn_total_percentage_estimated'] == 0

    second_test_product = mommy.make(Product, health_percentage=42)

    assert Product.objects.count() == 2

    third_result = determine_fvpn_share(second_test_product, category)

    assert 'ofcom_p_fvpn_mixed' not in third_result
    assert 'ofcom_p_fvpn' in third_result
    assert third_result['ofcom_p_fvpn'] == 2
    assert 'fvpn_total_percentage_estimated' in third_result
    assert third_result['fvpn_total_percentage_estimated'] == 42

    mommy.make(NutriScoreFacts, product=first_test_product, fruit_percentage=None, fruit_percentage_dried=4,
               vegetable_percentage=19, vegetable_percentage_dried=2, pulses_percentage=15, pulses_percentage_dried=10,
               nuts_percentage=8)

    assert NutriScoreFacts.objects.count() == 1

    fourth_result = determine_fvpn_share(first_test_product, category)

    assert 'ofcom_p_fvpn_mixed' not in fourth_result
    assert 'ofcom_p_fvpn' in fourth_result
    assert fourth_result['ofcom_p_fvpn'] == 0
    assert 'fvpn_total_percentage_estimated' in fourth_result
    assert fourth_result['fvpn_total_percentage_estimated'] == 0

    mommy.make(NutriScoreFacts, product=second_test_product, fruit_percentage=12, fruit_percentage_dried=4,
               vegetable_percentage=19, vegetable_percentage_dried=2, pulses_percentage=15, pulses_percentage_dried=10,
               nuts_percentage=8)

    assert NutriScoreFacts.objects.count() == 2

    fifth_result = determine_fvpn_share(second_test_product, category)

    assert 'ofcom_p_fvpn_mixed' not in fifth_result
    assert 'ofcom_p_fvpn' in fifth_result
    assert fifth_result['ofcom_p_fvpn'] == 10
    assert 'fvpn_total_percentage_estimated' in fifth_result
    assert fifth_result['fvpn_total_percentage_estimated'] > 74
