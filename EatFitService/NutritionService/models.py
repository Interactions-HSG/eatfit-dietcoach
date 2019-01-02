# -*- coding: utf-8 -*-

from django.db import models
from NutritionService.helpers import is_number
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.contrib.auth.models import User
import os
from uuid import uuid4

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
        return self.name_de

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
    icon = models.ImageField(upload_to="minor_category_icons", null=True, blank=True, verbose_name="Icon")

    def __unicode__(self):
        return self.name_de

    class Meta:
        db_table = 'minor_category'


class Product(models.Model):
    TRUSTBOX = 'Trustbox'
    OPENFOOD = 'Openfood'
    CROWDSOURCING = 'Crowdsourcing'
    CODECHECK = 'Codecheck'
    OPEN_WORLD = 'open_world'
    AUTO_ID_LABS = 'Auto-ID Labs'
    PRODUCT_SOURCES = (
        (TRUSTBOX, TRUSTBOX),
        (CROWDSOURCING, CROWDSOURCING),
        (OPENFOOD, OPENFOOD),
        (CODECHECK, CODECHECK),
        (OPEN_WORLD, OPEN_WORLD),
        (AUTO_ID_LABS, AUTO_ID_LABS),
    )
    id = models.BigAutoField(primary_key=True)
    gtin = models.BigIntegerField(unique=True)
    product_name_en = models.TextField(null=True, blank=True)
    product_name_de = models.TextField(null=True, blank=True)
    product_name_fr = models.TextField(null=True, blank=True)
    product_name_it = models.TextField(null=True, blank=True)
    producer = models.TextField(null=True, blank=True)
    major_category = models.ForeignKey(MajorCategory, on_delete=models.DO_NOTHING, null=True, editable=False)
    minor_category = models.ForeignKey(MinorCategory, on_delete=models.DO_NOTHING, null=True)
    product_size = models.CharField(max_length=255, null=True, blank=True)
    product_size_unit_of_measure = models.CharField(max_length=255, null=True, blank=True)
    serving_size = models.CharField(max_length=255, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to="product_images", null=True, blank=True)
    back_image = models.ImageField(upload_to="product_images", null=True, blank=True)
    original_image_url = models.TextField(null=True, blank=True)
    ofcom_value = models.IntegerField(null=True, blank=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    source_checked = models.BooleanField(default=False)  # Flag if the product source is trusted
    source = models.CharField(max_length=256, null=True, blank=True, choices=PRODUCT_SOURCES)
    health_percentage = models.FloatField(null=True, blank=True,
                                          validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
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
    processed = models.BooleanField(default = False)

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
    user = models.OneToOneField(User, primary_key=True, related_name = "partner")
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
    r2n_user_active = models.BooleanField(default = True)

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
        #unique_together = ('r2n_user', 'business_unit', 'receipt_id')
        verbose_name = "DigitalReceipt"
        verbose_name_plural = "DigitalReceipts"
        db_table = 'digital_receipt'


class Matching(models.Model):
    article_id = models.CharField(max_length=255)
    article_type = models.CharField(max_length=255)
    gtin = models.BigIntegerField()
    eatfit_product = models.ForeignKey(Product, null=True, blank=True, editable = False)

    def save(self, *args, **kwargs):
        if self.gtin:
            products = Product.objects.filter(gtin = self.gtin)
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
    counter = models.IntegerField(default=0, editable=False)

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

    nutrition_facts = NutritionFact.objects.filter(product = product)[:10]
    for fact in nutrition_facts:
        if fact.amount and fact.amount != 0:
            data_score = data_score + 1
    allergens = Allergen.objects.filter(product = product)
    for allergen in allergens:
        if allergen.certainity == "true" or allergen.certainity == "false":
            data_score = data_score + 1
        else:
            data_score = data_score - 0.5
    product.data_score = data_score

def calculate_ofcom_value(product):
    nutrition_facts = NutritionFact.objects.filter(product = product)
    data_quality_sufficient = True
    ofcom_value = 0
    for fact in nutrition_facts:
        converted, amount  = is_number(fact.amount)
        if not converted:
            data_quality_sufficient = False
            break
        amount = float(fact.amount)
        if fact.name == ENERGY_KJ:
            ofcom_value = ofcom_value + __calcluate_ofcom_point(amount, [3350, 3015, 2680, 2345, 2010, 1675, 1340, 1005, 670, 335])
        elif fact.name == SATURATED_FAT:
            ofcom_value = ofcom_value + __calcluate_ofcom_point(amount, [10, 9, 8, 7, 6, 5, 4, 3, 2, 1])
        elif fact.name == SUGARS:
            ofcom_value = ofcom_value + __calcluate_ofcom_point(amount, [45, 40, 36, 31, 27, 22.5, 18, 13.5, 9, 4.5])
        elif fact.name == SODIUM:
            if fact.unit_of_measure == "mg":
                ofcom_value = ofcom_value + __calcluate_ofcom_point(amount, [900, 810, 720, 630, 540, 450, 360, 270, 180, 90])
            elif fact.unit_of_measure == "g":
                ofcom_value = ofcom_value + __calcluate_ofcom_point(amount, [0.9, 0.81, 0.72, 0.63, 0.54, 0.45, 0.36, 0.27, 0.18, 0.09])
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