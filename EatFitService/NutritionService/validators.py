from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator

minimum_float_validator = MinValueValidator(0.0)
maximum_float_validator = MaxValueValidator(100.0)

retailer_id_validator = RegexValidator(regex=r'^[a-z]{2}.+$', message='Invalid ID pattern (Format: ch.coop)')
market_region_id_validator = RegexValidator(regex=r'^[A-Z]{2}$', message='Invalid ID pattern (Format: CH')
