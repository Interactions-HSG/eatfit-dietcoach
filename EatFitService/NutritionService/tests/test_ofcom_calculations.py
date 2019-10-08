from model_mommy import mommy
import pytest

from NutritionService.models import ADDED_FAT, BEVERAGE, CHEESE, FOOD, NutritionFact, Product, determine_ofcom_values, \
    added_fat_conversion
from NutritionService.nutriscore import score_tables
from NutritionService.nutriscore.calculations import calculate_nutrient_ofcom_value, calculate_total_ofcom_value, \
    calculate_nutriscore_beverage, calculate_nutriscore_non_beverage, calculate_negative_points


def test_energy_kj_beverage_score():
    """
    Original table:
    | Points | Calories (KJ) |
    |--------|---------------|
    | 0      | <= 0          |
    | 1      | <= 30         |
    | 2      | <= 60         |
    | 3      | <= 90         |
    | 4      | <= 120        |
    | 5      | <= 150        |
    | 6      | <= 180        |
    | 7      | <= 210        |
    | 8      | <= 240        |
    | 9      | <= 270        |
    | 10     | > 270         |
    """

    test_case_0 = 0
    test_case_1 = 30
    test_case_2 = 60
    test_case_3 = 90
    test_case_4 = 120
    test_case_5 = 150
    test_case_6 = 180
    test_case_7 = 210
    test_case_8 = 240
    test_case_9 = 270
    test_case_10 = 271

    case_0_result = calculate_nutrient_ofcom_value(score_tables.ENERGY_KJ_BEVERAGE_SCORES, test_case_0)
    case_1_result = calculate_nutrient_ofcom_value(score_tables.ENERGY_KJ_BEVERAGE_SCORES, test_case_1)
    case_2_result = calculate_nutrient_ofcom_value(score_tables.ENERGY_KJ_BEVERAGE_SCORES, test_case_2)
    case_3_result = calculate_nutrient_ofcom_value(score_tables.ENERGY_KJ_BEVERAGE_SCORES, test_case_3)
    case_4_result = calculate_nutrient_ofcom_value(score_tables.ENERGY_KJ_BEVERAGE_SCORES, test_case_4)
    case_5_result = calculate_nutrient_ofcom_value(score_tables.ENERGY_KJ_BEVERAGE_SCORES, test_case_5)
    case_6_result = calculate_nutrient_ofcom_value(score_tables.ENERGY_KJ_BEVERAGE_SCORES, test_case_6)
    case_7_result = calculate_nutrient_ofcom_value(score_tables.ENERGY_KJ_BEVERAGE_SCORES, test_case_7)
    case_8_result = calculate_nutrient_ofcom_value(score_tables.ENERGY_KJ_BEVERAGE_SCORES, test_case_8)
    case_9_result = calculate_nutrient_ofcom_value(score_tables.ENERGY_KJ_BEVERAGE_SCORES, test_case_9)
    case_10_result = calculate_nutrient_ofcom_value(score_tables.ENERGY_KJ_BEVERAGE_SCORES, test_case_10)

    assert test_case_0 <= 0
    assert case_0_result == 0

    assert test_case_1 <= 30
    assert case_1_result == 1

    assert test_case_2 <= 60
    assert case_2_result == 2

    assert test_case_3 <= 90
    assert case_3_result == 3

    assert test_case_4 <= 120
    assert case_4_result == 4

    assert test_case_5 <= 150
    assert case_5_result == 5

    assert test_case_6 <= 180
    assert case_6_result == 6

    assert test_case_7 <= 210
    assert case_7_result == 7

    assert test_case_8 <= 240
    assert case_8_result == 8

    assert test_case_9 <= 270
    assert case_9_result == 9

    assert test_case_10 > 270
    assert case_10_result == 10


def test_energy_kj_not_beverage_score():
    """
    Original table:
    | Points | Calories (KJ) |
    |--------|---------------|
    | 0      | <= 335        |
    | 1      | > 335         |
    | 2      | > 670         |
    | 3      | > 1005        |
    | 4      | > 1340        |
    | 5      | > 1340        |
    | 6      | > 2010        |
    | 7      | > 2345        |
    | 8      | > 2680        |
    | 9      | > 3015        |
    | 10     | > 3350        |
    """

    test_case_0 = -1
    test_case_1 = 336
    test_case_2 = 671
    test_case_3 = 1006
    test_case_4 = 1341
    test_case_5 = 1676
    test_case_6 = 2011
    test_case_7 = 2346
    test_case_8 = 2681
    test_case_9 = 3016
    test_case_10 = 3351

    case_0_result = calculate_nutrient_ofcom_value(score_tables.ENERGY_KJ_NOT_BEVERAGE_SCORES, test_case_0)
    case_1_result = calculate_nutrient_ofcom_value(score_tables.ENERGY_KJ_NOT_BEVERAGE_SCORES, test_case_1)
    case_2_result = calculate_nutrient_ofcom_value(score_tables.ENERGY_KJ_NOT_BEVERAGE_SCORES, test_case_2)
    case_3_result = calculate_nutrient_ofcom_value(score_tables.ENERGY_KJ_NOT_BEVERAGE_SCORES, test_case_3)
    case_4_result = calculate_nutrient_ofcom_value(score_tables.ENERGY_KJ_NOT_BEVERAGE_SCORES, test_case_4)
    case_5_result = calculate_nutrient_ofcom_value(score_tables.ENERGY_KJ_NOT_BEVERAGE_SCORES, test_case_5)
    case_6_result = calculate_nutrient_ofcom_value(score_tables.ENERGY_KJ_NOT_BEVERAGE_SCORES, test_case_6)
    case_7_result = calculate_nutrient_ofcom_value(score_tables.ENERGY_KJ_NOT_BEVERAGE_SCORES, test_case_7)
    case_8_result = calculate_nutrient_ofcom_value(score_tables.ENERGY_KJ_NOT_BEVERAGE_SCORES, test_case_8)
    case_9_result = calculate_nutrient_ofcom_value(score_tables.ENERGY_KJ_NOT_BEVERAGE_SCORES, test_case_9)
    case_10_result = calculate_nutrient_ofcom_value(score_tables.ENERGY_KJ_NOT_BEVERAGE_SCORES, test_case_10)

    assert test_case_0 <= 335
    assert case_0_result == 0

    assert test_case_1 > 335
    assert case_1_result == 1

    assert test_case_2 > 670
    assert case_2_result == 2

    assert test_case_3 > 1005
    assert case_3_result == 3

    assert test_case_4 > 1340
    assert case_4_result == 4

    assert test_case_5 > 1340
    assert case_5_result == 5

    assert test_case_6 > 2010
    assert case_6_result == 6

    assert test_case_7 > 2345
    assert case_7_result == 7

    assert test_case_8 > 2680
    assert case_8_result == 8

    assert test_case_9 > 3015
    assert case_9_result == 9

    assert test_case_10 > 3350
    assert case_10_result == 10


def test_sugars_beverage_score():
    """
    Original table:
    | Points | Sugars (g) |
    |--------|------------|
    | 0      | <= 0       |
    | 1      | <= 1.5     |
    | 2      | <= 3       |
    | 3      | <= 4.5     |
    | 4      | <= 6       |
    | 5      | <= 7.5     |
    | 6      | <= 9       |
    | 7      | <= 10.5    |
    | 8      | <= 12      |
    | 9      | <= 13.5    |
    | 10     | > 13.5     |
    """

    test_case_0 = 0
    test_case_1 = 1.5
    test_case_2 = 3
    test_case_3 = 4.5
    test_case_4 = 6
    test_case_5 = 7.5
    test_case_6 = 9
    test_case_7 = 10.5
    test_case_8 = 12
    test_case_9 = 13.5
    test_case_10 = 13.6

    case_0_result = calculate_nutrient_ofcom_value(score_tables.SUGARS_BEVERAGE_SCORES, test_case_0)
    case_1_result = calculate_nutrient_ofcom_value(score_tables.SUGARS_BEVERAGE_SCORES, test_case_1)
    case_2_result = calculate_nutrient_ofcom_value(score_tables.SUGARS_BEVERAGE_SCORES, test_case_2)
    case_3_result = calculate_nutrient_ofcom_value(score_tables.SUGARS_BEVERAGE_SCORES, test_case_3)
    case_4_result = calculate_nutrient_ofcom_value(score_tables.SUGARS_BEVERAGE_SCORES, test_case_4)
    case_5_result = calculate_nutrient_ofcom_value(score_tables.SUGARS_BEVERAGE_SCORES, test_case_5)
    case_6_result = calculate_nutrient_ofcom_value(score_tables.SUGARS_BEVERAGE_SCORES, test_case_6)
    case_7_result = calculate_nutrient_ofcom_value(score_tables.SUGARS_BEVERAGE_SCORES, test_case_7)
    case_8_result = calculate_nutrient_ofcom_value(score_tables.SUGARS_BEVERAGE_SCORES, test_case_8)
    case_9_result = calculate_nutrient_ofcom_value(score_tables.SUGARS_BEVERAGE_SCORES, test_case_9)
    case_10_result = calculate_nutrient_ofcom_value(score_tables.SUGARS_BEVERAGE_SCORES, test_case_10)

    assert test_case_0 <= 0
    assert case_0_result == 0

    assert test_case_1 <= 1.5
    assert case_1_result == 1

    assert test_case_2 <= 3
    assert case_2_result == 2

    assert test_case_3 <= 4.5
    assert case_3_result == 3

    assert test_case_4 <= 6
    assert case_4_result == 4

    assert test_case_5 <= 7.5
    assert case_5_result == 5

    assert test_case_6 <= 9
    assert case_6_result == 6

    assert test_case_7 <= 10.5
    assert case_7_result == 7

    assert test_case_8 <= 12
    assert case_8_result == 8

    assert test_case_9 <= 13.5
    assert case_9_result == 9

    assert test_case_10 > 13.5
    assert case_10_result == 10


def test_sugars_not_beverage_score():
    """
    Original table:
    | Points | Sugars (g) |
    |--------|------------|
    | 0      | <= 4.5     |
    | 1      | > 4.5      |
    | 2      | > 9        |
    | 3      | > 13.5     |
    | 4      | > 18       |
    | 5      | > 22.5     |
    | 6      | > 27       |
    | 7      | > 31       |
    | 8      | > 36       |
    | 9      | > 40       |
    | 10     | > 45       |
    """

    test_case_0 = 4.5
    test_case_1 = 4.6
    test_case_2 = 10
    test_case_3 = 13.6
    test_case_4 = 19
    test_case_5 = 22.6
    test_case_6 = 28
    test_case_7 = 32
    test_case_8 = 37
    test_case_9 = 41
    test_case_10 = 46

    case_0_result = calculate_nutrient_ofcom_value(score_tables.SUGARS_NOT_BEVERAGE_SCORES, test_case_0)
    case_1_result = calculate_nutrient_ofcom_value(score_tables.SUGARS_NOT_BEVERAGE_SCORES, test_case_1)
    case_2_result = calculate_nutrient_ofcom_value(score_tables.SUGARS_NOT_BEVERAGE_SCORES, test_case_2)
    case_3_result = calculate_nutrient_ofcom_value(score_tables.SUGARS_NOT_BEVERAGE_SCORES, test_case_3)
    case_4_result = calculate_nutrient_ofcom_value(score_tables.SUGARS_NOT_BEVERAGE_SCORES, test_case_4)
    case_5_result = calculate_nutrient_ofcom_value(score_tables.SUGARS_NOT_BEVERAGE_SCORES, test_case_5)
    case_6_result = calculate_nutrient_ofcom_value(score_tables.SUGARS_NOT_BEVERAGE_SCORES, test_case_6)
    case_7_result = calculate_nutrient_ofcom_value(score_tables.SUGARS_NOT_BEVERAGE_SCORES, test_case_7)
    case_8_result = calculate_nutrient_ofcom_value(score_tables.SUGARS_NOT_BEVERAGE_SCORES, test_case_8)
    case_9_result = calculate_nutrient_ofcom_value(score_tables.SUGARS_NOT_BEVERAGE_SCORES, test_case_9)
    case_10_result = calculate_nutrient_ofcom_value(score_tables.SUGARS_NOT_BEVERAGE_SCORES, test_case_10)

    assert test_case_0 <= 4.5
    assert case_0_result == 0

    assert test_case_1 > 4.5
    assert case_1_result == 1

    assert test_case_2 > 9
    assert case_2_result == 2

    assert test_case_3 > 13.5
    assert case_3_result == 3

    assert test_case_4 > 18
    assert case_4_result == 4

    assert test_case_5 > 22.5
    assert case_5_result == 5

    assert test_case_6 > 27
    assert case_6_result == 6

    assert test_case_7 > 31
    assert case_7_result == 7

    assert test_case_8 > 36
    assert case_8_result == 8

    assert test_case_9 > 40
    assert case_9_result == 9

    assert test_case_10 > 45
    assert case_10_result == 10


def test_saturated_fat_added_fat_score():
    """
    Original table:
    | Points | Total Saturated Fatty Acids / All Lipids (%) |
    |--------|----------------------------------------------|
    | 0      | < 10                                         |
    | 1      | < 16                                         |
    | 2      | < 22                                         |
    | 3      | < 28                                         |
    | 4      | < 34                                         |
    | 5      | < 40                                         |
    | 6      | < 46                                         |
    | 7      | < 52                                         |
    | 8      | < 58                                         |
    | 9      | < 64                                         |
    | 10     | >= 64                                        |
    """

    test_case_0 = 9
    test_case_1 = 15
    test_case_2 = 21
    test_case_3 = 27
    test_case_4 = 33
    test_case_5 = 39
    test_case_6 = 45
    test_case_7 = 51
    test_case_8 = 57
    test_case_9 = 63
    test_case_10 = 64

    case_0_result = calculate_nutrient_ofcom_value(score_tables.SATURATED_FAT_ADDED_FAT_SCORES, test_case_0)
    case_1_result = calculate_nutrient_ofcom_value(score_tables.SATURATED_FAT_ADDED_FAT_SCORES, test_case_1)
    case_2_result = calculate_nutrient_ofcom_value(score_tables.SATURATED_FAT_ADDED_FAT_SCORES, test_case_2)
    case_3_result = calculate_nutrient_ofcom_value(score_tables.SATURATED_FAT_ADDED_FAT_SCORES, test_case_3)
    case_4_result = calculate_nutrient_ofcom_value(score_tables.SATURATED_FAT_ADDED_FAT_SCORES, test_case_4)
    case_5_result = calculate_nutrient_ofcom_value(score_tables.SATURATED_FAT_ADDED_FAT_SCORES, test_case_5)
    case_6_result = calculate_nutrient_ofcom_value(score_tables.SATURATED_FAT_ADDED_FAT_SCORES, test_case_6)
    case_7_result = calculate_nutrient_ofcom_value(score_tables.SATURATED_FAT_ADDED_FAT_SCORES, test_case_7)
    case_8_result = calculate_nutrient_ofcom_value(score_tables.SATURATED_FAT_ADDED_FAT_SCORES, test_case_8)
    case_9_result = calculate_nutrient_ofcom_value(score_tables.SATURATED_FAT_ADDED_FAT_SCORES, test_case_9)
    case_10_result = calculate_nutrient_ofcom_value(score_tables.SATURATED_FAT_ADDED_FAT_SCORES, test_case_10)

    assert test_case_0 < 10
    assert case_0_result == 0

    assert test_case_1 < 16
    assert case_1_result == 1

    assert test_case_2 < 22
    assert case_2_result == 2

    assert test_case_3 < 28
    assert case_3_result == 3

    assert test_case_4 < 34
    assert case_4_result == 4

    assert test_case_5 < 40
    assert case_5_result == 5

    assert test_case_6 < 46
    assert case_6_result == 6

    assert test_case_7 < 52
    assert case_7_result == 7

    assert test_case_8 < 58
    assert case_8_result == 8

    assert test_case_9 < 64
    assert case_9_result == 9

    assert test_case_10 >= 64
    assert case_10_result == 10


def test_saturated_fat_not_added_fat_score():
    """
    Original table:
    | Points | Saturated Fatty Acids (g) |
    |--------|---------------------------|
    | 0      | <= 1                      |
    | 1      | > 1                       |
    | 2      | > 2                       |
    | 3      | > 3                       |
    | 4      | > 4                       |
    | 5      | > 5                       |
    | 6      | > 6                       |
    | 7      | > 7                       |
    | 8      | > 8                       |
    | 9      | > 9                       |
    | 10     | > 10                      |
    """

    test_case_0 = 1
    test_case_1 = 2
    test_case_2 = 3
    test_case_3 = 4
    test_case_4 = 5
    test_case_5 = 6
    test_case_6 = 7
    test_case_7 = 8
    test_case_8 = 9
    test_case_9 = 10
    test_case_10 = 11

    case_0_result = calculate_nutrient_ofcom_value(score_tables.SATURATED_FAT_NOT_ADDED_FAT_SCORES, test_case_0)
    case_1_result = calculate_nutrient_ofcom_value(score_tables.SATURATED_FAT_NOT_ADDED_FAT_SCORES, test_case_1)
    case_2_result = calculate_nutrient_ofcom_value(score_tables.SATURATED_FAT_NOT_ADDED_FAT_SCORES, test_case_2)
    case_3_result = calculate_nutrient_ofcom_value(score_tables.SATURATED_FAT_NOT_ADDED_FAT_SCORES, test_case_3)
    case_4_result = calculate_nutrient_ofcom_value(score_tables.SATURATED_FAT_NOT_ADDED_FAT_SCORES, test_case_4)
    case_5_result = calculate_nutrient_ofcom_value(score_tables.SATURATED_FAT_NOT_ADDED_FAT_SCORES, test_case_5)
    case_6_result = calculate_nutrient_ofcom_value(score_tables.SATURATED_FAT_NOT_ADDED_FAT_SCORES, test_case_6)
    case_7_result = calculate_nutrient_ofcom_value(score_tables.SATURATED_FAT_NOT_ADDED_FAT_SCORES, test_case_7)
    case_8_result = calculate_nutrient_ofcom_value(score_tables.SATURATED_FAT_NOT_ADDED_FAT_SCORES, test_case_8)
    case_9_result = calculate_nutrient_ofcom_value(score_tables.SATURATED_FAT_NOT_ADDED_FAT_SCORES, test_case_9)
    case_10_result = calculate_nutrient_ofcom_value(score_tables.SATURATED_FAT_NOT_ADDED_FAT_SCORES, test_case_10)

    assert test_case_0 <= 1
    assert case_0_result == 0

    assert test_case_1 > 1
    assert case_1_result == 1

    assert test_case_2 > 2
    assert case_2_result == 2

    assert test_case_3 > 3
    assert case_3_result == 3

    assert test_case_4 > 4
    assert case_4_result == 4

    assert test_case_5 > 5
    assert case_5_result == 5

    assert test_case_6 > 6
    assert case_6_result == 6

    assert test_case_7 > 7
    assert case_7_result == 7

    assert test_case_8 > 8
    assert case_8_result == 8

    assert test_case_9 > 9
    assert case_9_result == 9

    assert test_case_10 > 10
    assert case_10_result == 10


def test_sodium_score():
    """
    Original table:
    | Points | Sodium (mg) |
    |--------|-------------|
    | 0      | <= 90       |
    | 1      | > 90        |
    | 2      | > 180       |
    | 3      | > 270       |
    | 4      | > 360       |
    | 5      | > 450       |
    | 6      | > 540       |
    | 7      | > 630       |
    | 8      | > 720       |
    | 9      | > 810       |
    | 10     | > 900       |
    """

    test_case_0 = 0
    test_case_1 = 91
    test_case_2 = 181
    test_case_3 = 271
    test_case_4 = 361
    test_case_5 = 451
    test_case_6 = 541
    test_case_7 = 631
    test_case_8 = 721
    test_case_9 = 811
    test_case_10 = 901

    case_0_result = calculate_nutrient_ofcom_value(score_tables.SODIUM_SCORES, test_case_0)
    case_1_result = calculate_nutrient_ofcom_value(score_tables.SODIUM_SCORES, test_case_1)
    case_2_result = calculate_nutrient_ofcom_value(score_tables.SODIUM_SCORES, test_case_2)
    case_3_result = calculate_nutrient_ofcom_value(score_tables.SODIUM_SCORES, test_case_3)
    case_4_result = calculate_nutrient_ofcom_value(score_tables.SODIUM_SCORES, test_case_4)
    case_5_result = calculate_nutrient_ofcom_value(score_tables.SODIUM_SCORES, test_case_5)
    case_6_result = calculate_nutrient_ofcom_value(score_tables.SODIUM_SCORES, test_case_6)
    case_7_result = calculate_nutrient_ofcom_value(score_tables.SODIUM_SCORES, test_case_7)
    case_8_result = calculate_nutrient_ofcom_value(score_tables.SODIUM_SCORES, test_case_8)
    case_9_result = calculate_nutrient_ofcom_value(score_tables.SODIUM_SCORES, test_case_9)
    case_10_result = calculate_nutrient_ofcom_value(score_tables.SODIUM_SCORES, test_case_10)

    assert test_case_0 <= 90
    assert case_0_result == 0

    assert test_case_1 > 90
    assert case_1_result == 1

    assert test_case_2 > 180
    assert case_2_result == 2

    assert test_case_3 > 270
    assert case_3_result == 3

    assert test_case_4 > 360
    assert case_4_result == 4

    assert test_case_5 > 450
    assert case_5_result == 5

    assert test_case_6 > 540
    assert case_6_result == 6

    assert test_case_7 > 630
    assert case_7_result == 7

    assert test_case_8 > 720
    assert case_8_result == 8

    assert test_case_9 > 810
    assert case_9_result == 9

    assert test_case_10 > 900
    assert case_10_result == 10


def test_protein_score():
    """
    Original table:
    | Points | Protein (g) |
    |--------|-------------|
    | 0      | <= 1.6      |
    | 1      | > 1.6       |
    | 2      | > 3.2       |
    | 3      | > 4.8       |
    | 4      | > 6.4       |
    | 5      | > 8.0       |
    """

    test_case_0 = 1.5
    test_case_1 = 1.7
    test_case_2 = 3.3
    test_case_3 = 4.9
    test_case_4 = 6.5
    test_case_5 = 8.1

    case_0_result = calculate_nutrient_ofcom_value(score_tables.PROTEIN_SCORES, test_case_0)
    case_1_result = calculate_nutrient_ofcom_value(score_tables.PROTEIN_SCORES, test_case_1)
    case_2_result = calculate_nutrient_ofcom_value(score_tables.PROTEIN_SCORES, test_case_2)
    case_3_result = calculate_nutrient_ofcom_value(score_tables.PROTEIN_SCORES, test_case_3)
    case_4_result = calculate_nutrient_ofcom_value(score_tables.PROTEIN_SCORES, test_case_4)
    case_5_result = calculate_nutrient_ofcom_value(score_tables.PROTEIN_SCORES, test_case_5)

    assert test_case_0 <= 1.6
    assert case_0_result == 0

    assert test_case_1 > 1.6
    assert case_1_result == 1

    assert test_case_2 > 3.2
    assert case_2_result == 2

    assert test_case_3 > 4.8
    assert case_3_result == 3

    assert test_case_4 > 6.4
    assert case_4_result == 4

    assert test_case_5 > 8.0
    assert case_5_result == 5


def test_fvpn_beverage_score():
    """
    Original table:
    | Points  | Fruits, veg (%) |
    |---------|-----------------|
    | 0       | <= 40           |
    | 2       | > 40            |
    | 4       | > 60            |
    | 10      | > 80            |
    """

    test_case_0 = 40
    test_case_2 = 41
    test_case_4 = 61
    test_case_10 = 81

    case_0_result = calculate_nutrient_ofcom_value(score_tables.FVPN_BEVERAGE_SCORES, test_case_0)
    case_2_result = calculate_nutrient_ofcom_value(score_tables.FVPN_BEVERAGE_SCORES, test_case_2)
    case_4_result = calculate_nutrient_ofcom_value(score_tables.FVPN_BEVERAGE_SCORES, test_case_4)
    case_10_result = calculate_nutrient_ofcom_value(score_tables.FVPN_BEVERAGE_SCORES, test_case_10)

    assert test_case_0 <= 40
    assert case_0_result == 0

    assert test_case_2 > 40
    assert case_2_result == 2

    assert test_case_4 > 60
    assert case_4_result == 4

    assert test_case_10 > 80
    assert case_10_result == 10


def test_fvpn_not_beverage_score():
    """
    Original table:
    | Points  | Fruits, veg (%) |
    |---------|-----------------|
    | 0       | <= 40           |
    | 1       | > 40            |
    | 2       | > 60            |
    | 5       | > 80            |
    """

    test_case_0 = 40
    test_case_1 = 41
    test_case_2 = 61
    test_case_5 = 81

    case_0_result = calculate_nutrient_ofcom_value(score_tables.FVPN_NOT_BEVERAGE_SCORES, test_case_0)
    case_1_result = calculate_nutrient_ofcom_value(score_tables.FVPN_NOT_BEVERAGE_SCORES, test_case_1)
    case_2_result = calculate_nutrient_ofcom_value(score_tables.FVPN_NOT_BEVERAGE_SCORES, test_case_2)
    case_5_result = calculate_nutrient_ofcom_value(score_tables.FVPN_NOT_BEVERAGE_SCORES, test_case_5)

    assert test_case_0 <= 40
    assert case_0_result == 0

    assert test_case_1 > 40
    assert case_1_result == 1

    assert test_case_2 > 60
    assert case_2_result == 2

    assert test_case_5 > 80
    assert case_5_result == 5


def test_dietary_fiber_score():
    """
    Original table:
    | Points | Fiber (g) |
    |--------|-----------|
    | 0      | <= 0.9    |
    | 1      | > 0.9     |
    | 2      | > 1.9     |
    | 3      | > 2.8     |
    | 4      | > 3.7     |
    | 5      | > 4.7     |
    """

    test_case_0 = 0.9
    test_case_1 = 1
    test_case_2 = 2
    test_case_3 = 2.9
    test_case_4 = 3.8
    test_case_5 = 4.8

    case_0_result = calculate_nutrient_ofcom_value(score_tables.DIETARY_FIBER_SCORES, test_case_0)
    case_1_result = calculate_nutrient_ofcom_value(score_tables.DIETARY_FIBER_SCORES, test_case_1)
    case_2_result = calculate_nutrient_ofcom_value(score_tables.DIETARY_FIBER_SCORES, test_case_2)
    case_3_result = calculate_nutrient_ofcom_value(score_tables.DIETARY_FIBER_SCORES, test_case_3)
    case_4_result = calculate_nutrient_ofcom_value(score_tables.DIETARY_FIBER_SCORES, test_case_4)
    case_5_result = calculate_nutrient_ofcom_value(score_tables.DIETARY_FIBER_SCORES, test_case_5)

    assert test_case_0 <= 0.9
    assert case_0_result == 0

    assert test_case_1 > 0.9
    assert case_1_result == 1

    assert test_case_2 > 1.9
    assert case_2_result == 2

    assert test_case_3 > 2.8
    assert case_3_result == 3

    assert test_case_4 > 3.7
    assert case_4_result == 4

    assert test_case_5 > 4.7
    assert case_5_result == 5

    
@pytest.mark.django_db
def test_all_beverage_calculations():
    """
    Test cases:
    1) energyKJ
    2) saturatedFat
    3) sugars
    4) dietaryFiber
    5) protein
    6) sodium
    """
    assert Product.objects.count() == 0
    assert NutritionFact.objects.count() == 0

    test_product = mommy.make(Product)
    mommy.make(NutritionFact, product=test_product, name='energyKJ', amount=280.2, unit_of_measure='kj')
    mommy.make(NutritionFact, product=test_product, name='saturatedFat', amount=5.3, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='sugars', amount=11.6, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='dietaryFiber', amount=2.1, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='protein', amount=7.4, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='sodium', amount=620, unit_of_measure='mg')

    assert Product.objects.count() == 1
    assert NutritionFact.objects.count() == 6

    test_nutrients = list(NutritionFact.objects.all())
    test_category = BEVERAGE

    ofcom_calculations = determine_ofcom_values(test_nutrients, test_category, test_product)

    energy_kj = ofcom_calculations['ofcom_n_energy_kj']
    saturated_fat = ofcom_calculations['ofcom_n_saturated_fat']
    sugars = ofcom_calculations['ofcom_n_sugars']
    dietary_fiber = ofcom_calculations['ofcom_p_dietary_fiber']
    protein = ofcom_calculations['ofcom_p_protein']
    sodium = ofcom_calculations['ofcom_n_salt']

    assert energy_kj == 10
    assert saturated_fat == 5
    assert sugars == 8
    assert dietary_fiber == 2
    assert protein == 4
    assert sodium == 6


@pytest.mark.django_db
def test_all_cheese_calculations():
    """
    Test cases:
    1) energyKJ
    2) saturatedFat
    3) sugars
    4) dietaryFiber
    5) protein
    6) sodium
    """
    assert Product.objects.count() == 0
    assert NutritionFact.objects.count() == 0

    test_product = mommy.make(Product)
    mommy.make(NutritionFact, product=test_product, name='energyKJ', amount=2280.2, unit_of_measure='kj')
    mommy.make(NutritionFact, product=test_product, name='saturatedFat', amount=7.8, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='sugars', amount=2.1, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='dietaryFiber', amount=4.2, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='protein', amount=99999.9, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='sodium', amount=900.0, unit_of_measure='mg')

    assert Product.objects.count() == 1
    assert NutritionFact.objects.count() == 6

    test_nutrients = list(NutritionFact.objects.all())
    test_category = CHEESE

    ofcom_calculations = determine_ofcom_values(test_nutrients, test_category, test_product)

    energy_kj = ofcom_calculations['ofcom_n_energy_kj']
    saturated_fat = ofcom_calculations['ofcom_n_saturated_fat']
    sugars = ofcom_calculations['ofcom_n_sugars']
    dietary_fiber = ofcom_calculations['ofcom_p_dietary_fiber']
    protein = ofcom_calculations['ofcom_p_protein']
    sodium = ofcom_calculations['ofcom_n_salt']

    assert energy_kj == 6
    assert saturated_fat == 7
    assert sugars == 0
    assert dietary_fiber == 4
    assert protein == 5
    assert sodium == 9


@pytest.mark.django_db
def test_added_fat_conversion():
    """
    Test cases:
    1) Unit of measure is not 'g'
    2) No NutritionFact object named 'totalFat'
    3) Multiple objects with name 'totalFat' found
    4) 'totalFat' amount is 0
    5) 'totalFat' amount is None
    6) Successful conversion
    """
    assert Product.objects.count() == 0
    assert NutritionFact.objects.count() == 0

    first_test_product = mommy.make(Product)
    mommy.make(NutritionFact, product=first_test_product, name='totalFat', amount=66.0)

    second_test_product = mommy.make(Product)
    mommy.make(NutritionFact, product=second_test_product, name='randomNutrient', amount=66.0, unit_of_measure='g')

    third_test_product = mommy.make(Product)
    mommy.make(NutritionFact, product=third_test_product, name='totalFat', amount=66.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=third_test_product, name='totalFat', amount=67.0, unit_of_measure='g')

    fourth_test_product = mommy.make(Product)
    mommy.make(NutritionFact, product=fourth_test_product, name='totalFat', amount=0.0, unit_of_measure='g')

    fifth_test_product = mommy.make(Product)
    mommy.make(NutritionFact, product=fifth_test_product, name='totalFat', amount=None, unit_of_measure='g')

    sixth_test_product = mommy.make(Product)
    mommy.make(NutritionFact, product=sixth_test_product, name='totalFat', amount=66.0, unit_of_measure='g')

    test_amount = 66.0

    assert Product.objects.count() == 6
    assert NutritionFact.objects.count() == 7

    first_test_result = added_fat_conversion(test_amount, first_test_product)
    second_test_result = added_fat_conversion(test_amount, second_test_product)
    third_test_result = added_fat_conversion(test_amount, third_test_product)
    fourth_test_result = added_fat_conversion(test_amount, fourth_test_product)
    fifth_test_result = added_fat_conversion(test_amount, fifth_test_product)
    sixth_test_result = added_fat_conversion(test_amount, sixth_test_product)

    assert not first_test_result
    assert not second_test_result
    assert not third_test_result
    assert not fourth_test_result
    assert not fifth_test_result
    assert sixth_test_result == 100.0


@pytest.mark.django_db
def test_all_added_fat_calculations():
    """
    Test cases:
    1) energyKJ
    2) saturatedFat
    3) sugars
    4) dietaryFiber
    5) protein
    6) sodium
    """
    assert Product.objects.count() == 0
    assert NutritionFact.objects.count() == 0

    test_product = mommy.make(Product)
    mommy.make(NutritionFact, product=test_product, name='energyKJ', amount=1000.0, unit_of_measure='kj')
    mommy.make(NutritionFact, product=test_product, name='saturatedFat', amount=6.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='sugars', amount=27.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='dietaryFiber', amount=1.9, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='protein', amount=4.7, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='sodium', amount=450.0, unit_of_measure='mg')
    mommy.make(NutritionFact, product=test_product, name='totalFat', amount=10.0, unit_of_measure='g')

    assert Product.objects.count() == 1
    assert NutritionFact.objects.count() == 7

    test_nutrients = list(NutritionFact.objects.all().exclude(name='totalFat'))
    test_category = ADDED_FAT

    ofcom_calculations = determine_ofcom_values(test_nutrients, test_category, test_product)

    energy_kj = ofcom_calculations['ofcom_n_energy_kj']
    saturated_fat = ofcom_calculations['ofcom_n_saturated_fat']
    sugars = ofcom_calculations['ofcom_n_sugars']
    dietary_fiber = ofcom_calculations['ofcom_p_dietary_fiber']
    protein = ofcom_calculations['ofcom_p_protein']
    sodium = ofcom_calculations['ofcom_n_salt']

    assert energy_kj == 2
    assert saturated_fat == 9
    assert sugars == 5
    assert dietary_fiber == 1
    assert protein == 2
    assert sodium == 4


@pytest.mark.django_db
def test_all_food_calculations():
    """
    Test cases:
    1) energyKJ
    2) saturatedFat
    3) sugars
    4) dietaryFiber
    5) protein
    6) sodium
    """
    assert Product.objects.count() == 0
    assert NutritionFact.objects.count() == 0

    test_product = mommy.make(Product)
    mommy.make(NutritionFact, product=test_product, name='energyKJ', amount=2700.0, unit_of_measure='kj')
    mommy.make(NutritionFact, product=test_product, name='saturatedFat', amount=4.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='sugars', amount=36.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='dietaryFiber', amount=5.0, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='protein', amount=1.5, unit_of_measure='g')
    mommy.make(NutritionFact, product=test_product, name='sodium', amount=600.0, unit_of_measure='mg')

    assert Product.objects.count() == 1
    assert NutritionFact.objects.count() == 6

    test_nutrients = list(NutritionFact.objects.all())
    test_category = FOOD

    ofcom_calculations = determine_ofcom_values(test_nutrients, test_category, test_product)

    energy_kj = ofcom_calculations['ofcom_n_energy_kj']
    saturated_fat = ofcom_calculations['ofcom_n_saturated_fat']
    sugars = ofcom_calculations['ofcom_n_sugars']
    dietary_fiber = ofcom_calculations['ofcom_p_dietary_fiber']
    protein = ofcom_calculations['ofcom_p_protein']
    sodium = ofcom_calculations['ofcom_n_salt']

    assert energy_kj == 8
    assert saturated_fat == 3
    assert sugars == 7
    assert dietary_fiber == 5
    assert protein == 0
    assert sodium == 6


def test_calculate_negative_points():
    energy_kj = 8
    saturated_fat = 3
    sugars = 7
    sodium = 6

    result = calculate_negative_points(energy_kj, sugars, saturated_fat, sodium)
    assert result == 24


def test_total_ofcom_value():
    """
    Test cases:
    1) fvpn_value < 5 and category != 'Cheese'
    2) fvpn_value == 5
    3) category == 'Cheese'
    """
    category = FOOD
    energy_kj = 8
    saturated_fat = 3
    sugars = 7
    sodium = 6
    dietary_fiber = 5
    protein = 2
    fvpn_value = 1

    negative_points = calculate_negative_points(energy_kj, sugars, saturated_fat, sodium)
    assert negative_points == 24

    first_result = calculate_total_ofcom_value(category, negative_points, fvpn_value, protein, dietary_fiber)
    assert first_result == 18

    fvpn_value = 5
    second_result = calculate_total_ofcom_value(category, negative_points, fvpn_value, protein, dietary_fiber)
    assert second_result == 12

    fvpn_value = 2
    category = CHEESE
    third_result = calculate_total_ofcom_value(category, negative_points, fvpn_value, protein, dietary_fiber)
    assert third_result == 15


def test_nutriscore_calculations():
    first_ofcom_value = -1
    second_ofcom_value = 2
    third_ofcom_value = 9
    fourth_ofcom_value = 11
    fifth_ofcom_value = 20

    first_result_beverage = calculate_nutriscore_beverage(first_ofcom_value)
    second_result_beverage = calculate_nutriscore_beverage(second_ofcom_value)
    third_result_beverage = calculate_nutriscore_beverage(third_ofcom_value)
    fourth_result_beverage = calculate_nutriscore_beverage(fourth_ofcom_value)
    fifth_result_beverage = calculate_nutriscore_beverage(fifth_ofcom_value)

    assert first_result_beverage == 'B'
    assert second_result_beverage == 'C'
    assert third_result_beverage == 'D'
    assert fourth_result_beverage == 'E'
    assert fifth_result_beverage == 'E'

    first_result_non_beverage = calculate_nutriscore_non_beverage(first_ofcom_value)
    second_result_non_beverage = calculate_nutriscore_non_beverage(second_ofcom_value)
    third_result_non_beverage = calculate_nutriscore_non_beverage(third_ofcom_value)
    fourth_result_non_beverage = calculate_nutriscore_non_beverage(fourth_ofcom_value)
    fifth_result_non_beverage = calculate_nutriscore_non_beverage(fifth_ofcom_value)

    assert first_result_non_beverage == 'A'
    assert second_result_non_beverage == 'B'
    assert third_result_non_beverage == 'C'
    assert fourth_result_non_beverage == 'D'
    assert fifth_result_non_beverage == 'E'
