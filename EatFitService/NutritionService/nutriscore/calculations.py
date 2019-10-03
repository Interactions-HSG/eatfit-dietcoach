from __future__ import division
import pint

# Allow conversions from volume to mass and vice-versa

context_name = 'eatfit'
volume = '[volume]'
mass = '[mass]'

ureg = pint.UnitRegistry()

# Add kilojoule as kj to defined units
ureg.define('kj = kilojoule')

context = pint.Context(context_name)


def mass_to_volume(unit_registry, x):
    # Assumption: 1g = 1ml
    density = unit_registry.gram / unit_registry.ml
    return x / density


def volume_to_mass(unit_registry, x):
    # Assumption: 1ml = 1mg
    density = unit_registry.gram / unit_registry.ml
    return x * density


context.add_transformation(volume, mass, volume_to_mass)
context.add_transformation(mass, volume, mass_to_volume)
ureg.add_context(context)

quantify = ureg.Quantity


def unit_of_measure_conversion(magnitude, current_unit, target_unit):
    """
    :param magnitude: float
    :param current_unit: str
    :param target_unit: str
    :return: float
    """
    if not isinstance(magnitude, float):
        # pint accepts string as input for magnitude, therefore we must restrict it to floats
        raise TypeError

    if current_unit == target_unit:
        return magnitude

    current_quantity = quantify(magnitude, current_unit)
    target_quantity = current_quantity.to(target_unit, context_name)

    return target_quantity.magnitude


def calculate_fvpn_percentage(fruit_percentage, fruit_percentage_dried, vegetable_percentage,
                              vegetable_percentage_dried, pulses_percentage, pulses_percentage_dried, nuts_percentage):
    normal_sum = fruit_percentage + vegetable_percentage + pulses_percentage + nuts_percentage
    dried_sum = fruit_percentage_dried + vegetable_percentage_dried + pulses_percentage_dried
    return min(100, (normal_sum + (2 * dried_sum)) / (100 + dried_sum))  # Value should not be > 100


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
