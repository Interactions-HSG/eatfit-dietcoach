# -*- coding: utf-8 -*-

import os
from uuid import uuid4
from toolz import itertoolz

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from rest_framework.authtoken.models import Token

from NutritionService.helpers import is_number, merge_dicts
from NutritionService.nutriscore import calculations
from NutritionService.nutriscore.score_tables import SCORE_TABLES_MAP
from NutritionService.validators import minimum_float_validator, maximum_float_validator

ENERGY_KJ = "energyKJ"
ENERGY_KCAL = "energyKcal"
TOTAL_FAT = "totalFat"
SATURATED_FAT = "saturatedFat"
TOTAL_CARBOHYDRATE = "totalCarbohydrate"
SUGARS = "sugars"
DIETARY_FIBER = "dietaryFiber"
PROTEIN = "protein"
SALT = "salt"
SODIUM = "sodium"

MINERAL_WATER = "Mineral Water"
BEVERAGE = "Beverage"
CHEESE = "Cheese"
ADDED_FAT = "Added Fat"
FOOD = "Food"
NO_FOOD = "No Food"
UNKNOWN = "Unknown"

NUTRISCORE_CATEGORIES = (
    (MINERAL_WATER, MINERAL_WATER),
    (BEVERAGE, BEVERAGE),
    (CHEESE, CHEESE),
    (ADDED_FAT, ADDED_FAT),
    (FOOD, FOOD),
    (NO_FOOD, NO_FOOD),
    (UNKNOWN, UNKNOWN),
)


def path_and_rename(instance, filename):
    base_path = "crowdsoure_images/"
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}.{}'.format(instance.pk, ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(base_path, filename)


# categories requested. Careful: Changed IDs changed to autifields and integerers, charfield for minor in snipped


class MajorCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name_de = models.TextField(max_length=1024, blank=True, null=True)
    name_en = models.TextField(max_length=1024, blank=True, null=True)
    name_it = models.TextField(max_length=1024, blank=True, null=True)
    name_fr = models.TextField(max_length=1024, blank=True, null=True)

    def __unicode__(self):
        if self.name_de:
            return self.name_de
        return 'NO_NAME_DE'

    class Meta:
        db_table = 'major_category'


class MinorCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name_de = models.TextField(max_length=1024, blank=True, null=True)
    name_en = models.TextField(max_length=1024, blank=True, null=True)
    name_it = models.TextField(max_length=1024, blank=True, null=True)
    name_fr = models.TextField(max_length=1024, blank=True, null=True)
    category_major = models.ForeignKey(MajorCategory, on_delete=models.DO_NOTHING, null=True)
    nwd_subcategory_id = models.CharField(max_length=255, blank=True, null=True)
    nutri_score_category = models.CharField(max_length=50, blank=True, null=True, choices=NUTRISCORE_CATEGORIES)
    icon = models.ImageField(upload_to="minor_category_icons", null=True, blank=True, verbose_name="Icon")

    def __unicode__(self):
        if self.name_de:
            return self.name_de
        return 'NO_NAME_DE'

    class Meta:
        db_table = 'minor_category'


class Product(models.Model):
    TRUSTBOX = 'Trustbox'
    OPENFOOD = 'Openfood'
    CROWDSOURCING = 'Crowdsourcing'
    CODECHECK = 'Codecheck'
    OPEN_WORLD = 'open_world'
    AUTO_ID_LABS = 'Auto-ID Labs'
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'

    PRODUCT_SOURCES = (
        (TRUSTBOX, TRUSTBOX),
        (CROWDSOURCING, CROWDSOURCING),
        (OPENFOOD, OPENFOOD),
        (CODECHECK, CODECHECK),
        (OPEN_WORLD, OPEN_WORLD),
        (AUTO_ID_LABS, AUTO_ID_LABS),
    )
    NUTRISCORE_SCORES = (
        (A, A),
        (B, B),
        (C, C),
        (D, D),
        (E, E),
    )
    id = models.BigAutoField(primary_key=True)
    gtin = models.BigIntegerField(unique=True)
    product_name_en = models.TextField(null=True, blank=True)
    product_name_de = models.TextField(null=True, blank=True)
    product_name_fr = models.TextField(null=True, blank=True)
    product_name_it = models.TextField(null=True, blank=True)
    producer = models.TextField(null=True, blank=True)
    major_category = models.ForeignKey(MajorCategory, on_delete=models.DO_NOTHING, null=True, editable=False)
    minor_category = models.ForeignKey(MinorCategory, on_delete=models.DO_NOTHING, null=True, blank=True)
    product_size = models.CharField(max_length=255, null=True, blank=True)
    product_size_unit_of_measure = models.CharField(max_length=255, null=True, blank=True)
    serving_size = models.CharField(max_length=255, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to="product_images", null=True, blank=True)
    back_image = models.ImageField(upload_to="product_images", null=True, blank=True)
    original_image_url = models.TextField(null=True, blank=True)
    nutri_score_category_estimated = models.CharField(max_length=50, blank=True, null=True,
                                                      choices=NUTRISCORE_CATEGORIES)
    nutri_score_final = models.CharField(max_length=1, null=True, blank=True, choices=NUTRISCORE_SCORES)
    nutri_score_by_manufacturer = models.CharField(max_length=1, null=True, blank=True, choices=NUTRISCORE_SCORES)
    nutri_score_calculated = models.CharField(max_length=1, null=True, blank=True, choices=NUTRISCORE_SCORES)
    nutri_score_calculated_mixed = models.CharField(max_length=1, null=True, blank=True, choices=NUTRISCORE_SCORES)
    nutri_score_quality_comment = models.TextField(null=True, blank=True)
    ofcom_value = models.IntegerField(null=True, blank=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    source_checked = models.BooleanField(default=False)  # Flag if the product source is trusted
    source = models.CharField(max_length=256, null=True, blank=True, choices=PRODUCT_SOURCES)
    health_percentage = models.FloatField(null=True, blank=True,
                                          validators=[minimum_float_validator, maximum_float_validator],
                                          verbose_name='Fruit, Vegetable, Nuts Share')
    quality_checked = models.DateTimeField(null=True, blank=True)
    automatic_update = models.BooleanField(default=True)
    data_score = models.FloatField(null=True, blank=True)
    found_count = models.IntegerField(default=0, editable=False)

    def save(self, *args, **kwargs):
        calculate_ofcom_value(self)
        calculate_data_score(self)
        if self.minor_category:
            self.major_category = self.minor_category.category_major
        super(Product, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        db_table = 'product'


class Retailer(models.Model):

    MIGROS = 'Migros'
    COOP = 'Coop'
    DENNER = 'Denner'
    FARMY = 'Farmy'
    VOLG = 'Volg'
    EDEKA = 'Edeka'

    RETAILER_CHOICES = (
        (MIGROS, MIGROS),
        (COOP, COOP),
        (DENNER, DENNER),
        (FARMY, FARMY),
        (VOLG, VOLG),
        (EDEKA, EDEKA),
    )

    retailer_name = models.CharField(max_length=20, choices=RETAILER_CHOICES)
    product = models.ForeignKey(Product, related_name='retailer')

    class Meta:
        verbose_name = 'Retailer'
        verbose_name_plural = 'Retailers'
        db_table = 'retailers'

    def __unicode__(self):
        return self.retailer_name


class MarketRegion(models.Model):

    SWITZERLAND = 'Switzerland'
    GERMANY = 'Germany'
    AUSTRIA = 'Austria'
    FRANCE = 'France'
    ITALY = 'Italy'

    MARKET_REGIONS = (
        (SWITZERLAND, SWITZERLAND),
        (GERMANY, GERMANY),
        (AUSTRIA, AUSTRIA),
        (FRANCE, FRANCE),
        (ITALY, ITALY),
    )

    MARKET_REGION_QUERY_MAP = {'ch': SWITZERLAND, 'de': GERMANY, 'au': AUSTRIA, 'fr': FRANCE, 'it': ITALY}

    market_region_name = models.CharField(max_length=52, choices=MARKET_REGIONS)
    product = models.ForeignKey(Product, related_name='market_region')

    class Meta:
        verbose_name = 'Market Region'
        verbose_name_plural = 'Market Regions'
        db_table = 'market_region'

    def __unicode__(self):
        return self.market_region_name


class AdditionalImage(models.Model):
    product = models.ForeignKey(Product, related_name='additional_image')
    image = models.ImageField(upload_to="product_images", null=True, blank=True)
    source = models.CharField(max_length=100, null=True, blank=True)
    image_url = models.URLField()

    class Meta:
        verbose_name = 'Additional Image'
        verbose_name_plural = 'Additional Images'
        db_table = 'additional_image'


class NutriScoreFacts(models.Model):
    product = models.OneToOneField(Product, related_name='nutri_score_fact', on_delete=models.CASCADE)
    # fvpn is an abbreviation for fruits, vegetables, pulses and nuts
    fvpn_total_percentage = models.FloatField(blank=True, null=True, validators=[minimum_float_validator,
                                                                                 maximum_float_validator])
    fvpn_total_percentage_estimated = models.FloatField(blank=True, null=True,
                                                        validators=[minimum_float_validator, maximum_float_validator])
    fruit_percentage = models.FloatField(blank=True, null=True,
                                             validators=[minimum_float_validator, maximum_float_validator])
    fruit_percentage_dried = models.FloatField(blank=True, null=True,
                                                   validators=[minimum_float_validator, maximum_float_validator])
    vegetable_percentage = models.FloatField(blank=True, null=True,
                                             validators=[minimum_float_validator, maximum_float_validator])
    vegetable_percentage_dried = models.FloatField(blank=True, null=True,
                                                   validators=[minimum_float_validator, maximum_float_validator])
    pulses_percentage = models.FloatField(blank=True, null=True,
                                          validators=[minimum_float_validator, maximum_float_validator])
    pulses_percentage_dried = models.FloatField(blank=True, null=True,
                                                validators=[minimum_float_validator, maximum_float_validator])
    nuts_percentage = models.FloatField(blank=True, null=True,
                                        validators=[minimum_float_validator, maximum_float_validator])
    ofcom_n_energy_kj = models.FloatField(blank=True, null=True)
    ofcom_n_saturated_fat = models.FloatField(blank=True, null=True)
    ofcom_n_sugars = models.FloatField(blank=True, null=True)
    ofcom_n_salt = models.FloatField(blank=True, null=True)
    ofcom_p_protein = models.FloatField(blank=True, null=True)
    ofcom_p_fvpn = models.FloatField(blank=True, null=True)
    ofcom_p_dietary_fiber = models.FloatField(blank=True, null=True)
    ofcom_n_energy_kj_mixed = models.FloatField(blank=True, null=True)
    ofcom_n_saturated_fat_mixed = models.FloatField(blank=True, null=True)
    ofcom_n_sugars_mixed = models.FloatField(blank=True, null=True)
    ofcom_n_salt_mixed = models.FloatField(blank=True, null=True)
    ofcom_p_protein_mixed = models.FloatField(blank=True, null=True)
    ofcom_p_fvpn_mixed = models.FloatField(blank=True, null=True)
    ofcom_p_dietary_fiber_mixed = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name = 'Nutri-Score Facts'
        verbose_name_plural = 'Nutri-Score Facts'
        db_table = 'nutri_score_fact'

    def __unicode__(self):
        return unicode(self.product.gtin)


class ErrorLog(models.Model):
    gtin = models.BigIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    reporting_app = models.CharField(max_length=256, null=True, blank=True)
    error_description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return str(self.gtin)

    class Meta:
        verbose_name = "Error Log"
        verbose_name_plural = "Error Logs"
        db_table = 'error_log'


class ImportErrorLog(models.Model):
    import_type = models.CharField(max_length=50)
    file_name = models.CharField(max_length=150)
    row_data = models.TextField()
    error_field = models.CharField(max_length=50)
    error_message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.filename

    class Meta:
        verbose_name = 'Import Error Log'
        verbose_name_plural = 'Import Error Logs'
        db_table = 'import_error'


class Allergen(models.Model):

    TRUE = 'true'
    FALSE = 'false'
    MAY_CONTAIN = 'mayContain'

    CERTAINTY_CHOICES = (
        (TRUE, TRUE),
        (FALSE, FALSE),
        (MAY_CONTAIN, MAY_CONTAIN),
    )

    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='allergens')
    name = models.CharField(max_length=64, null=True, blank=True)
    certainity = models.CharField(max_length=11, choices=CERTAINTY_CHOICES, null=True, blank=True)

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
    is_mixed = models.BooleanField(default=False)

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
    processed = models.BooleanField(default=False)

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
    front_image = models.ImageField(upload_to=path_and_rename, null=True, blank=True)
    back_image = models.ImageField(upload_to=path_and_rename, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    health_percentage = models.FloatField(null=True, blank=True,
                                          validators=[minimum_float_validator, maximum_float_validator],
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

    ingredient_en = models.TextField(blank=True, null=True)
    ingredient_de = models.TextField(blank=True, null=True)
    ingredient_fr = models.TextField(blank=True, null=True)
    ingredient_it = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name

    def __getitem__(self, key):
        return getattr(self, key)

    class Meta:
        verbose_name = "Crowdsource Product"
        verbose_name_plural = "Crowdsource Products"
        db_table = 'crowdsource_product'


class NutrientName(models.Model):
    name = models.CharField(max_length=255, verbose_name="Name", primary_key=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "Nutrient Name"
        verbose_name_plural = "Nutrient Names"
        db_table = 'nutrient_name'


class HealthTipp(models.Model):
    text_de = models.TextField(null=True, blank=True)
    text_en = models.TextField(null=True, blank=True)
    text_fr = models.TextField(null=True, blank=True)
    text_it = models.TextField(null=True, blank=True)
    minor_categories = models.ManyToManyField(MinorCategory, related_name='minor_category', blank=True)
    nutrients = models.ManyToManyField(NutrientName, related_name='nutrients', blank=True)
    image = models.ImageField(upload_to="health_tipp_images", null=True, blank=True)

    def __unicode__(self):
        return self.text_de

    class Meta:
        verbose_name = "Health Tipp"
        verbose_name_plural = "Health Tipps"
        db_table = 'health_tipp'


class ReceiptToNutritionPartner(models.Model):
    user = models.OneToOneField(User, primary_key=True, related_name="partner")
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "ReceiptToNutritionPartner"
        verbose_name_plural = "ReceiptToNutritionPartners"
        db_table = 'receipt_to_nutrition_partner'


class ReceiptToNutritionUser(models.Model):
    r2n_partner = models.ForeignKey(ReceiptToNutritionPartner)
    r2n_username = models.CharField(max_length=255)
    r2n_user_active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.r2n_username

    class Meta:
        unique_together = ('r2n_partner', 'r2n_username',)
        verbose_name = "ReceiptToNutritionUser"
        verbose_name_plural = "ReceiptToNutritionUsers"
        db_table = 'receipt_to_nutrition_user'


class DigitalReceipt(models.Model):
    r2n_user = models.ForeignKey(ReceiptToNutritionUser)
    business_unit = models.CharField(max_length=255)
    receipt_id = models.CharField(max_length=255)
    article_id = models.CharField(max_length=255)
    article_type = models.CharField(max_length=255)
    quantity = models.FloatField()
    quantity_unit = models.CharField(max_length=255)
    price = models.FloatField()
    price_currency = models.CharField(max_length=255)
    receipt_datetime = models.DateTimeField()

    def __unicode__(self):
        return self.article_id

    class Meta:
        # unique_together = ('r2n_user', 'business_unit', 'receipt_id')
        verbose_name = "DigitalReceipt"
        verbose_name_plural = "DigitalReceipts"
        db_table = 'digital_receipt'


class Matching(models.Model):
    article_id = models.CharField(max_length=255)
    article_type = models.CharField(max_length=255)
    gtin = models.BigIntegerField()
    eatfit_product = models.ForeignKey(Product, null=True, blank=True, editable=False)

    def save(self, *args, **kwargs):
        if self.gtin:
            products = Product.objects.filter(gtin=self.gtin)
            if products.exists():
                product = products[0]
                self.eatfit_product = product
        super(Matching, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.article_id

    class Meta:
        verbose_name = "Matching"
        verbose_name_plural = "Matchings"
        db_table = 'matching'


class NonFoundMatching(models.Model):
    article_id = models.CharField(max_length=255)
    article_type = models.CharField(max_length=255)
    business_unit = models.CharField(max_length=255)
    price_per_unit = models.FloatField()
    counter = models.IntegerField(default=0)

    class Meta:
        verbose_name = "NonFoundMatching"
        verbose_name_plural = "NonFoundMatchings"
        db_table = 'non_found_matching'


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


def calculate_data_score(product):
    data_score = 0
    if product.product_name_de and product.product_name_de != "":
        data_score = data_score + 10
    if product.image:
        data_score = data_score + 10
    if product.major_category:
        data_score = data_score + 5
    if product.minor_category:
        data_score = data_score + 5
    if product.health_percentage and product.health_percentage != 0:
        data_score = data_score + 5

    nutrition_facts = NutritionFact.objects.filter(product=product)[:10]
    for fact in nutrition_facts:
        if fact.amount and fact.amount != 0:
            data_score = data_score + 1
    allergens = Allergen.objects.filter(product=product)
    for allergen in allergens:
        if allergen.certainity == "true" or allergen.certainity == "false":
            data_score = data_score + 1
        else:
            data_score = data_score - 0.5
    product.data_score = data_score


def calculate_ofcom_value(product):
    all_nutrition_facts = NutritionFact.objects.filter(product=product)

    nutrition_facts = []
    nf_grouped_name = itertoolz.groupby(lambda x: x.name, list(all_nutrition_facts))
    for key, value in nf_grouped_name.items():
        name_grouped_mixed = itertoolz.groupby(lambda x: x.is_mixed, value)
        if True in name_grouped_mixed:
            nutrition_facts.append(name_grouped_mixed[True][0])
        else:
            nutrition_facts.append(name_grouped_mixed[False][0])

    data_quality_sufficient = True
    ofcom_value = 0
    for fact in nutrition_facts:
        converted, amount = is_number(fact.amount)
        if not converted:
            data_quality_sufficient = False
            break
        amount = float(fact.amount)
        if fact.name == ENERGY_KJ:
            ofcom_value = ofcom_value + __calcluate_ofcom_point(amount,
                                                                [3350, 3015, 2680, 2345, 2010, 1675, 1340, 1005, 670,
                                                                 335])
        elif fact.name == SATURATED_FAT:
            ofcom_value = ofcom_value + __calcluate_ofcom_point(amount, [10, 9, 8, 7, 6, 5, 4, 3, 2, 1])
        elif fact.name == SUGARS:
            ofcom_value = ofcom_value + __calcluate_ofcom_point(amount, [45, 40, 36, 31, 27, 22.5, 18, 13.5, 9, 4.5])
        elif fact.name == SODIUM:
            if fact.unit_of_measure == "mg":
                ofcom_value = ofcom_value + __calcluate_ofcom_point(amount,
                                                                    [900, 810, 720, 630, 540, 450, 360, 270, 180, 90])
            elif fact.unit_of_measure == "g":
                ofcom_value = ofcom_value + __calcluate_ofcom_point(amount,
                                                                    [0.9, 0.81, 0.72, 0.63, 0.54, 0.45, 0.36, 0.27,
                                                                     0.18, 0.09])
            else:
                data_quality_sufficient = False
                break
        elif fact.name == DIETARY_FIBER:
            ofcom_value = ofcom_value - __calcluate_ofcom_point(amount, [3.5, 2.8, 2.1, 1.4, 0.7])
        elif fact.name == PROTEIN:
            ofcom_value = ofcom_value - __calcluate_ofcom_point(amount, [8, 6.4, 4.8, 3.2, 1.6])
    if data_quality_sufficient:
        product.ofcom_value = ofcom_value


def __calcluate_ofcom_point(amount, values):
    points = len(values)
    for value in values:
        if amount > value:
            return points
        points = points - 1
    return 0


def get_nutri_score_category(product):
    """
    :param product: Product (Django ORM-object)
    :return: str
    """
    if product.minor_category is None:
        ErrorLog.objects.create(gtin=product.gtin, reporting_app='Eatfit_NS',
                                error_description='Minor category is missing.')
        if product.nutri_score_category_estimated is None:
            return 'Food'
        else:
            return product.nutri_score_category_estimated

    if product.minor_category.nutri_score_category is None:
        ErrorLog.objects.create(gtin=product.gtin, reporting_app='Eatfit_NS',
                                error_description='Minor category does not have nutri score category assigned.')

        if product.nutri_score_category_estimated is None:
            return 'Food'
        else:
            return product.nutri_score_category_estimated

    return product.minor_category.nutri_score_category


def get_and_validate_nutrients(product):
    """
    :param product: Product (Django ORM-object)
    :return: list
    """
    nutrients = list(NutritionFact.objects.filter(product=product))
    nutrient_data = {
        ENERGY_KJ: 'kj',
        SATURATED_FAT: 'g',
        SUGARS: 'g',
        DIETARY_FIBER: 'g',
        PROTEIN: 'g',
        SODIUM: 'mg'
    }
    errors = []
    valid_nutrients = []
    for nutrient in nutrients:
        if nutrient.name not in nutrient_data.keys():
            errors.append(
                ErrorLog(gtin=product.gtin,
                         reporting_app='Eatfit_NS',
                         error_description='{} is missing'.format(nutrient.name))
            )

        converted, _ = is_number(nutrient.amount)
        if not converted:
            errors.append(
                ErrorLog(gtin=product.gtin,
                         reporting_app='Eatfit_NS',
                         error_description='Amount of {} is not valid'.format(nutrient.name))
            )

        target_unit = nutrient_data.get(nutrient.name, None)
        if target_unit is not None and target_unit != nutrient.unit_of_measure:
            amount = calculations.unit_of_measure_conversion(nutrient.amount, nutrient.unit_of_measure, target_unit)
            if amount is not None:
                nutrient.amount = amount
                nutrient.unit_of_measure = target_unit
            else:
                errors.append(
                    ErrorLog(gtin=product.gtin,
                             reporting_app='Eatfit_NS',
                             error_description='Measurement unit of {} is not valid'.format(nutrient.name))
                )

        valid_nutrients.append(nutrient)
    ErrorLog.objects.bulk_create(errors)
    return valid_nutrients


def reduce_nutrients(nutrients, gtin):
    """
    :param nutrients: list
    :param gtin: int
    :return: list
    """
    nutrients_grouped_by_name = itertoolz.groupby(lambda x: x.name, nutrients)
    errors = []
    valid_nutrients = []
    for key, value in nutrients_grouped_by_name.items():
        if len(value) > 1:
            errors.append(
                ErrorLog(gtin=gtin,
                         reporting_app='Eatfit_NS',
                         error_description='Multiple entries for {}'.format(key))
            )

        valid_nutrients.append(value[-1])
    ErrorLog.objects.bulk_create(errors)
    return valid_nutrients


def separate_nutrients(grouped_nutrients, gtin):
    """
    :param grouped_nutrients: dict
    :param gtin: int
    :return: tuple of lists
    """
    nutrition_facts_mixed = []
    nutrition_facts_not_mixed = []
    for nutrient in grouped_nutrients:
        if nutrient.is_mixed:
            nutrition_facts_mixed.append(nutrient)
        else:
            nutrition_facts_not_mixed.append(nutrient)

    nutrition_facts_mixed = reduce_nutrients(nutrition_facts_mixed, gtin)
    nutrition_facts_not_mixed = reduce_nutrients(nutrition_facts_not_mixed, gtin)
    return nutrition_facts_mixed, nutrition_facts_not_mixed


def added_fat_conversion(amount, product):
    try:
        total_fat = NutritionFact.objects.get(product=product, name=TOTAL_FAT, unit_of_measure='g')
        return 100 * (amount / total_fat.amount)
    except (ObjectDoesNotExist, MultipleObjectsReturned, ZeroDivisionError, TypeError):
        return


def determine_ofcom_values(nutrients, category, product, mixed=False):
    """
    :param nutrients: list
    :param category: str
    :param product: Product (Django ORM-object)
    :param mixed: bool
    :return: dict
    """
    ofcom_values_catgegories = {
        ENERGY_KJ: {
            True: 'ofcom_n_energy_kj_mixed',
            False: 'ofcom_n_energy_kj'
        },
        SATURATED_FAT: {
            True: 'ofcom_n_saturated_fat_mixed',
            False: 'ofcom_n_saturated_fat'
        },
        SUGARS: {
            True: 'ofcom_n_sugars_mixed',
            False: 'ofcom_n_sugars'
        },
        SODIUM: {
            True: 'ofcom_n_sodium_mixed',
            False: 'ofcom_n_sodium'
        },
        PROTEIN: {
            True: 'ofcom_p_protein_mixed',
            False: 'ofcom_p_protein'
        },
        DIETARY_FIBER: {
            True: 'ofcom_p_dietary_fiber_mixed',
            False: 'ofcom_p_dietary_fiber'
        }
    }
    scores_table = SCORE_TABLES_MAP[category]
    nutri_score_facts_kwargs = {}

    for nutrient in nutrients:
        scores = scores_table[nutrient.name]
        if category == ADDED_FAT and nutrient.name == SATURATED_FAT:
            amount = added_fat_conversion(nutrient.amount, product)
        else:
            amount = nutrient.amount
        if amount:
            field = ofcom_values_catgegories[nutrient.name][mixed]
            ofcom_value = calculations.calculate_nutrient_ofcom_value(scores, amount)
            nutri_score_facts_kwargs.update({field: ofcom_value})

    return nutri_score_facts_kwargs


def determine_fvpn_share(product, mixed=False):
    """
    :param product: Product (Django ORM-object)
    :param mixed: bool
    :return: float
    """
    nutri_score_fact_fvpn_kwargs = {}
    if mixed:
        nutri_score_fact_fvpn_kwargs.update({'ofcom_p_fvpn_mixed': 0})
        return nutri_score_fact_fvpn_kwargs
    try:
        nutri_score_fact = NutriScoreFacts.objects.get(product=product)
        fruit_percentage = nutri_score_fact.fruit_percentage
        fruit_percentage_dried = nutri_score_fact.fruit_percentage_dried
        pulses_percentage = nutri_score_fact.pulses_percentage
        pulses_percentage_dried = nutri_score_fact.pulses_percentage_dried
        vegetable_percentage = nutri_score_fact.vegetable_percentage
        vegetable_percentage_dried = nutri_score_fact.vegetable_percentage_dried
        nuts_percentage = nutri_score_fact.nuts_percentage
        params = [fruit_percentage, fruit_percentage_dried, pulses_percentage, pulses_percentage_dried,
                  vegetable_percentage,
                  vegetable_percentage_dried, nuts_percentage]
        if None in params:
            fvpn_share = 0
        else:
            fvpn_share = calculations.calculate_fvpn_percentage(fruit_percentage, fruit_percentage_dried,
                                                                pulses_percentage, pulses_percentage_dried,
                                                                vegetable_percentage,
                                                                vegetable_percentage, nuts_percentage)
    except ObjectDoesNotExist:
        if product.health_percentage:
            fvpn_share = product.health_percentage
        else:
            fvpn_share = 0

    nutri_score_fact_fvpn_kwargs.update({'ofcom_p_fvpn': fvpn_share})
    return nutri_score_fact_fvpn_kwargs


def nutriscore_calculations(nutrients, product, category, mixed=False):
    """
    :param nutrients: list
    :param product: Product (Django ORM-object)
    :param category: str
    :param mixed: bool
    :return: tuple of float, str
    """
    nutri_score_facts = determine_ofcom_values(nutrients, category, product, mixed=mixed)
    fvpn = determine_fvpn_share(product, mixed=mixed)
    nutri_score_facts_kwargs = merge_dicts(nutri_score_facts, fvpn)
    NutriScoreFacts.objects.update_or_create(product=product, **nutri_score_facts_kwargs)

    energy_kj = nutri_score_facts_kwargs.get('ofcom_n_energy_kj', None)
    sugars = nutri_score_facts_kwargs.get('ofcom_n_sugars', None)
    saturated_fat = nutri_score_facts_kwargs.get('ofcom_n_saturated_fat', None)
    sodium = nutri_score_facts_kwargs.get('sodium', None)

    fvpn_value = nutri_score_facts_kwargs.get('ofcom_p_fvpn', 0)
    protein = nutri_score_facts_kwargs.get('protein', 0)
    dietary_fiber = nutri_score_facts_kwargs.get('dietary_fiber', 0)

    if None in [energy_kj, sugars, saturated_fat, sodium]:
        return

    negative_points = calculations.calculate_negative_points(energy_kj, sugars, saturated_fat, sodium)
    total_ofcom_value = calculations.calculate_total_ofcom_value(category, negative_points, fvpn_value, protein, dietary_fiber)

    if category == BEVERAGE:
        nutri_score = calculations.calculate_nutriscore_beverage(total_ofcom_value)
    else:
        nutri_score = calculations.calculate_nutriscore_non_beverage(total_ofcom_value)

    return total_ofcom_value, nutri_score


def nutriscore_main(product):
    category = get_nutri_score_category(product)

    if category not in [MINERAL_WATER, BEVERAGE, CHEESE, ADDED_FAT, FOOD]:
        return

    if category == MINERAL_WATER:
        product.ofcom_value = -15
        product.nutri_score_calculated = 'A'
    else:
        nutrients_grouped = get_and_validate_nutrients(product)
        mixed_nutrients, nutrients = separate_nutrients(nutrients_grouped, product.gtin)
        _, nutri_score_mixed = nutriscore_calculations(mixed_nutrients, product, category, mixed=True)
        ofcom_score, nutri_score = nutriscore_calculations(nutrients, product, category)

        product.ofcom_score = ofcom_score
        product.nutri_score_calculated = nutri_score
        product.nutri_score_mixed = nutri_score_mixed
