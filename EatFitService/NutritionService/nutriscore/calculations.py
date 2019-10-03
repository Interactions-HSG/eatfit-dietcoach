from __future__ import division


def unit_of_measure_conversion(amount, current_unit, target_unit):
    """
    Assumption: 1g = 1ml
    """
    conversion_map = {
        'kg': 3,
        'cl': 2,
        'dl': 1,
        'g': 0,
        'ml': 0,
        'mg': -3
    }

    try:
        exponent = conversion_map[current_unit] - conversion_map[target_unit]
    except KeyError:
        return

    return amount * (10 ** exponent)


def calculate_fvpn_percentage(fruit_percentage, fruit_percentage_dried, vegetable_percentage,
                              vegetable_percentage_dried, pulses_percentage, pulses_percentage_dried, nuts_percentage):
    normal_sum = fruit_percentage + vegetable_percentage + pulses_percentage + nuts_percentage
    dried_sum = fruit_percentage_dried + vegetable_percentage_dried + pulses_percentage_dried
    return min(100, 100 * (normal_sum + (2 * dried_sum)) / (100 + dried_sum))  # Value should not be > 100


def calculate_nutrient_ofcom_value(score_table, amount):
    for score, value in score_table.items():
        if amount <= value:
            return score
    return list(score_table.keys())[-1]


def calculate_negative_points(energy_kj, sugars, saturated_fat, sodium):
    return energy_kj + sugars + saturated_fat + sodium


def calculate_total_ofcom_value(category, negative_points, fvpn_value, protein, dietary_fiber):
    if fvpn_value < 5 and category != 'Cheese':
        return negative_points - fvpn_value - dietary_fiber
    return negative_points - protein - fvpn_value - dietary_fiber


def calculate_nutriscore_beverage(ofcom_value):
    if ofcom_value <= 1:
        return 'B'
    elif ofcom_value < 6:
        return 'C'
    elif ofcom_value < 10:
        return 'D'
    else:
        return 'E'


def calculate_nutriscore_non_beverage(ofcom_value):
    if ofcom_value <= -1:
        return 'A'
    elif ofcom_value < 3:
        return 'B'
    elif ofcom_value < 11:
        return 'C'
    elif ofcom_value < 19:
        return 'D'
    else:
        return 'E'
