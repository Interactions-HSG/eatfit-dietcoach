from django.core.validators import MaxValueValidator, MinValueValidator, FileExtensionValidator

minimum_float_validator = MinValueValidator(0.0)
maximum_float_validator = MaxValueValidator(100.0)

csv_validator = FileExtensionValidator(allowed_extensions=['csv'])
