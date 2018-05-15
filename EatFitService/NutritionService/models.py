# -*- coding: utf-8 -*-

from django.db import models
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings

# categories requested. Careful: Changed IDs changed to autifields and integerers, charfield for minor in snipped
class MajorCategory(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.TextField(max_length=1024, blank=True, null=True)
    canonical_name = models.TextField(max_length=1024, blank=True, null=True)

    def __unicode__(self):
        return self.description

    class Meta:
        db_table = 'major_category'


class MinorCategory(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.TextField(max_length=1024, blank=True, null=True)
    category_major = models.ForeignKey(MajorCategory, on_delete=models.DO_NOTHING, null=True)
    nwd_subcategory_id = models.CharField(max_length=255, blank=True, null=True)
    icon = models.ImageField(upload_to="minor_category_icons", null=True, blank=True, verbose_name="Icon")

    def __unicode__(self):
        return self.description

    class Meta:
        db_table = 'minor_category'


class Product(models.Model):
    TRUSTBOX = 'Trustbox'
    OPENFOOD = 'Openfood'
    CROWDSOURCING = 'Crowdsourcing'
    CODECHECK = 'Codecheck'
    AUTO_ID_LABS = 'Auto-ID Labs'
    PRODUCT_SOURCES = (
        (TRUSTBOX, TRUSTBOX),
        (CROWDSOURCING, CROWDSOURCING),
        (OPENFOOD, OPENFOOD),
        (CODECHECK, CODECHECK),
        (AUTO_ID_LABS, AUTO_ID_LABS),
    )
    id = models.BigAutoField(primary_key=True)
    gtin = models.BigIntegerField()
    product_name_en = models.TextField(null=True, blank=True)
    product_name_de = models.TextField(null=True, blank=True)
    product_name_fr = models.TextField(null=True, blank=True)
    product_name_it = models.TextField(null=True, blank=True)
    producer = models.TextField(null=True, blank=True)
    major_category = models.ForeignKey(MajorCategory, on_delete=models.DO_NOTHING, null=True)
    minor_category = models.ForeignKey(MinorCategory, on_delete=models.DO_NOTHING, null=True)
    product_size = models.CharField(max_length=255, null=True, blank=True)
    product_size_unit_of_measure = models.CharField(max_length=255, null=True, blank=True)
    serving_size = models.CharField(max_length=255, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to="product_images", null=True, blank=True)
    original_image_url = models.TextField(null=True, blank=True)
    ofcom_value = models.IntegerField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    source_checked = models.BooleanField(default=False)  # Flag if the product source is trusted
    source = models.CharField(max_length=256, null=True, blank=True, choices=PRODUCT_SOURCES)
    health_percentage = models.FloatField(null=True, blank=True,
                                          validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
                                          verbose_name='Fruit, Vegetable, Nuts Share')

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        db_table = 'product'


class ErrorLog(models.Model):
    gtin = models.BigIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    reporting_app = models.CharField(max_length=256, null=True, blank=True)
    error_description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Error Log"
        verbose_name_plural = "Error Logs"
        db_table = 'error_log'


class Allergen(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='allergens')
    name = models.CharField(max_length=64, null=True, blank=True)
    certainity = models.TextField()
    
    class Meta:
        verbose_name = 'Allergen'
        verbose_name_plural = 'Allergens'
        db_table = 'allergen'


class NutritionFact(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='nutrients')
    name = models.CharField(max_length=64, null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    unit_of_measure = models.CharField(max_length=8, null=True, blank=True)

    class Meta:
        verbose_name = 'NutritionFact'
        verbose_name_plural = 'NutritionFacts'
        db_table = 'nutrition_fact'


class Ingredient(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='ingredients')
    lang = models.CharField(max_length=2)
    text = models.TextField()

    class Meta:
        verbose_name = "ingridient"
        verbose_name_plural = "ingridients"
        db_table = 'ingredient'


class NotFoundLog(models.Model):
    id = models.AutoField(primary_key=True)
    gtin = models.BigIntegerField()
    count = models.BigIntegerField(default=1)
    first_searched_for = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'not_found_log'


class ImportLog(models.Model):
    id = models.AutoField(primary_key=True)
    import_started = models.DateTimeField()
    import_finished = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'import_log'


class CrowdsourceProduct(models.Model):
    name = models.CharField(max_length=255, verbose_name="Name")  # Required when creating
    gtin = models.BigIntegerField(verbose_name="GTIN", unique=True)  # Required when creating - can never change!
    product_name_en = models.TextField(null=True, blank=True)
    product_name_de = models.TextField(null=True, blank=True)
    product_name_fr = models.TextField(null=True, blank=True)
    product_name_it = models.TextField(null=True, blank=True)
    producer = models.TextField(null=True, blank=True)
    major_category = models.ForeignKey(MajorCategory, on_delete=models.DO_NOTHING, null=True, blank=True)
    minor_category = models.ForeignKey(MinorCategory, on_delete=models.DO_NOTHING, null=True, blank=True)
    product_size = models.CharField(max_length=255, null=True, blank=True)
    product_size_unit_of_measure = models.CharField(max_length=255, null=True, blank=True)
    serving_size = models.CharField(max_length=255, null=True, blank=True, verbose_name="Serving Size")
    comment = models.TextField(null=True, blank=True)
    front_image = models.ImageField(upload_to="crowdsoure_images", null=True, blank=True)
    back_image = models.ImageField(upload_to="crowdsoure_images", null=True, blank=True)
    # ofcom_value = models.IntegerField(null=True, blank=True)  # Calcuate when creating the model
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # source = models.CharField() - this by default will be crowdsource and will be set when adding it to the Product.
    health_percentage = models.FloatField(null=True, blank=True,
                                          validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
                                          verbose_name='Fruit, Vegetable, Nuts Share')

    # Will create new nutrition entries when creating the Product model entry.
    salt = models.FloatField(verbose_name="Salz pro 100g/ml in Gramm", blank=True, null=True)
    sodium = models.FloatField(verbose_name="Natrium pro 100g/ml in Gramm", blank=True, null=True)
    energy = models.FloatField(verbose_name="Energie pro 100g/ml in KJ", blank=True, null=True)
    fat = models.FloatField(verbose_name="Fett pro 100g/ml in Gramm", blank=True, null=True)
    saturated_fat = models.FloatField(verbose_name="Gesättigtes Fett pro 100g/ml in Gramm", blank=True, null=True)
    carbohydrate = models.FloatField(verbose_name="Kohlenhydrate pro 100g/ml in Gramm", blank=True, null=True)
    sugar = models.FloatField(verbose_name="davon Zucker pro 100g/ml in Gramm", blank=True, null=True)
    fibers = models.FloatField(verbose_name="Ballaststoffe pro 100g/ml in Gramm", blank=True, null=True)
    protein = models.FloatField(verbose_name="Protein pro 100g/ml in Gramm", blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "Crowdsource Product"
        verbose_name_plural = "Crowdsource Products"
        db_table = 'crowdsource_product'


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)