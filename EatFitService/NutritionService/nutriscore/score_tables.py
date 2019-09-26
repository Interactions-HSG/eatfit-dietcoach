from collections import OrderedDict

INF = float('inf')

ENERGY_KJ_BEVERAGE_SCORES = OrderedDict([  # Base unit of measure: KJ
    (0, 0),
    (1, 30),
    (2, 60),
    (3, 90),
    (4, 120),
    (5, 150),
    (6, 180),
    (7, 210),
    (8, 240),
    (9, 270),
    (10, INF)
])

ENERGY_KJ_NOT_BEVERAGE_SCORES = OrderedDict([  # Base unit of measure: KJ
    (0, 335),
    (1, 670),
    (2, 1005),
    (3, 1340),
    (4, 1675),
    (5, 2010),
    (6, 2345),
    (7, 2680),
    (8, 3015),
    (9, 3350),
    (10, INF),
])

SUGARS_BEVERAGE_SCORES = OrderedDict([  # Base unit of measure: g
    (0, 0),
    (1, 1.5),
    (2, 3),
    (3, 4.5),
    (4, 6),
    (5, 7.5),
    (6, 9),
    (7, 10.5),
    (8, 12),
    (9, 13.5),
    (10, INF),
])

SUGARS_NOT_BEVERAGE_SCORES = OrderedDict([  # Base unit of measure: g
    (0, 4.5),
    (1, 9),
    (2, 13.5),
    (3, 18),
    (4, 22.5),
    (5, 27),
    (6, 31),
    (7, 36),
    (8, 40),
    (9, 45),
    (10, INF),
])

SATURATED_FAT_ADDED_FAT_SCORES = OrderedDict([  # Base unit of measure: % (100 * saturatedFat/totalFat)
    (0, 9),
    (1, 15),
    (2, 21),
    (3, 27),
    (4, 33),
    (5, 39),
    (6, 45),
    (7, 51),
    (8, 57),
    (9, 63),
    (10, 100),
])

SATURATED_FAT_NOT_ADDED_FAT_SCORES = OrderedDict([  # Base unit of measure: g
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 8),
    (8, 9),
    (9, 10),
    (10, INF),
])

SODIUM_SCORES = OrderedDict([  # Base unit of measure: mg
    (0, 90),
    (1, 180),
    (2, 270),
    (3, 360),
    (4, 450),
    (5, 540),
    (6, 630),
    (7, 720),
    (8, 810),
    (9, 900),
    (10, INF),
])

PROTEIN_SCORES = OrderedDict([  # Base unit of measure: g
    (0, 1.6),
    (1, 3.2),
    (2, 4.8),
    (3, 6.4),
    (4, 8.0),
    (5, INF),
])

FVPN_BEVERAGE_SCORES = OrderedDict([  # Base unit of measure: %
    (0, 40),
    (2, 60),
    (4, 80),
    (10, 100),
])

FVPN_NOT_BEVERAGE_SCORES = OrderedDict([  # Base unit of measure: %
    (0, 40),
    (1, 60),
    (2, 80),
    (5, 100),
])

DIETARY_FIBER_SCORES = OrderedDict([  # Base unit of measure: g
    (0, 0.9),
    (1, 1.9),
    (2, 2.8),
    (3, 3.7),
    (4, 4.7),
    (5, INF),
])

SCORE_TABLES_MAP = {
    'Beverage': {
        'energyKJ': ENERGY_KJ_BEVERAGE_SCORES,
        'saturatedFat': SATURATED_FAT_NOT_ADDED_FAT_SCORES,
        'sugars': SUGARS_BEVERAGE_SCORES,
        'dietaryFiber': DIETARY_FIBER_SCORES,
        'protein': PROTEIN_SCORES,
        'sodium': SODIUM_SCORES,
        'fvpn': FVPN_BEVERAGE_SCORES
    },
    'Cheese': {
        'energyKJ': ENERGY_KJ_NOT_BEVERAGE_SCORES,
        'saturatedFat': SATURATED_FAT_NOT_ADDED_FAT_SCORES,
        'sugars': SUGARS_NOT_BEVERAGE_SCORES,
        'dietaryFiber': DIETARY_FIBER_SCORES,
        'protein': PROTEIN_SCORES,
        'sodium': SODIUM_SCORES,
        'fvpn': FVPN_NOT_BEVERAGE_SCORES
    },
    'Added Fat': {
        'energyKJ': ENERGY_KJ_NOT_BEVERAGE_SCORES,
        'saturatedFat': SATURATED_FAT_ADDED_FAT_SCORES,
        'sugars': SUGARS_NOT_BEVERAGE_SCORES,
        'dietaryFiber': DIETARY_FIBER_SCORES,
        'protein': PROTEIN_SCORES,
        'sodium': SODIUM_SCORES,
        'fvpn': FVPN_NOT_BEVERAGE_SCORES
    },
    'Food': {
        'energyKJ': ENERGY_KJ_NOT_BEVERAGE_SCORES,
        'saturatedFat': SATURATED_FAT_NOT_ADDED_FAT_SCORES,
        'sugars': SUGARS_NOT_BEVERAGE_SCORES,
        'dietaryFiber': DIETARY_FIBER_SCORES,
        'protein': PROTEIN_SCORES,
        'sodium': SODIUM_SCORES,
        'fvpn': FVPN_NOT_BEVERAGE_SCORES
    }
}
