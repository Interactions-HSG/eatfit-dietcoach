#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.conf import settings

class ImportLog(models.Model):
    import_timestamp = models.DateTimeField()
    successful = models.BooleanField()
    failed_reason = models.TextField(max_length=500, blank=True, null=True)
    product_gtin = models.TextField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = 'import_log'

class LmpCategory(models.Model):
    lmp_id = models.IntegerField(primary_key=True)
    description = models.TextField(max_length=1024, blank=True, null=True)
    canonical_name = models.TextField(max_length=1024, blank=True, null=True)

    class Meta:
        db_table = 'lmp_category'


class Nutrition(models.Model):
    product = models.OneToOneField('Product', primary_key=True)

    class Meta:
        db_table = 'nutrition'


class NutritionAttribute(models.Model):
    value = models.CharField(max_length=4000, blank=True, null=True)
    language_code = models.CharField(max_length=255, blank=True, null=True)
    country_code = models.CharField(max_length=255, blank=True, null=True)
    canonical_name = models.TextField(max_length=4000, blank=True, null=True)
    nutrition = models.ForeignKey(Nutrition, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'nutrition_attribute'


class NutritionFact(models.Model):
    amount = models.CharField(max_length=255, blank=True, null=True)
    unit_of_measure = models.CharField(max_length=255, blank=True, null=True)
    combined_amount_and_measure = models.TextField(max_length=1024, blank=True, null=True)
    daily_percent = models.CharField(max_length=255, blank=True, null=True)
    language_code = models.CharField(max_length=255, blank=True, null=True)
    country_code = models.CharField(max_length=255, blank=True, null=True)
    canonical_name = models.TextField(max_length=4000, blank=True, null=True)
    nutrition_facts_group = models.ForeignKey('NutritionFactsGroup', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'nutrition_fact'


class NutritionFactsGroup(models.Model):
    nutrition = models.OneToOneField('Nutrition', primary_key=True)

    class Meta:
        db_table = 'nutrition_facts_group'


class NutritionGroupAttribute(models.Model):
    value = models.CharField(max_length=4000, blank=True, null=True)
    language_code = models.CharField(max_length=255, blank=True, null=True)
    country_code = models.CharField(max_length=255, blank=True, null=True)
    canonical_name = models.TextField(max_length=1024, blank=True, null=True)
    nutrition_facts_group = models.ForeignKey(NutritionFactsGroup, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'nutrition_group_attribute'


class NutritionLabel(models.Model):
    value = models.TextField(max_length=4000, blank=True, null=True)
    label_id = models.IntegerField(blank=True, null=True)
    nutrition = models.ForeignKey(Nutrition, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'nutrition_label'


class NwdMainCategory(models.Model):
    nwd_main_category_id = models.IntegerField(primary_key=True)
    description = models.TextField(max_length=1024, blank=True, null=True)
    canonical_name = models.TextField(max_length=1024, blank=True, null=True)

    class Meta:
        db_table = 'nwd_main_category'


class NwdMainCategoryMinNutritionFactDifference(models.Model):
    min_absolute = models.FloatField(blank=True, null=True)
    min_relative = models.IntegerField(blank=True, null=True)
    nutrition_fact_canonical_name = models.TextField(max_length=1024)
    nwd_main_category = models.ForeignKey(NwdMainCategory, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'nwd_main_category_min_nutrition_fact_difference'


class NwdSubcategory(models.Model):
    nwd_subcategory_id = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(max_length=1024, blank=True, null=True)
    nwd_main_category = models.ForeignKey(NwdMainCategory, models.DO_NOTHING, blank=True, null=True)
    lmp = models.ForeignKey(LmpCategory, models.DO_NOTHING, blank=True, null=True)

    def __unicode__(self):
        return self.description

    class Meta:
        db_table = 'nwd_subcategory'


class NwdSubcategoryMinNutritionFactDifference(models.Model):
    min_absolute = models.FloatField(blank=True, null=True)
    min_relative = models.IntegerField(blank=True, null=True)
    nutrition_fact_canonical_name = models.CharField(max_length=255)
    nwd_subcategory = models.ForeignKey(NwdSubcategory, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'nwd_subcategory_min_nutrition_fact_difference'


class Product(models.Model):
    target_market_country_code = models.SmallIntegerField(blank=True, null=True)
    gln = models.BigIntegerField(blank=True, null=True)
    gtin = models.BigIntegerField()
    status = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.CharField(max_length=255, blank=True, null=True)
    nwd_main_category = models.ForeignKey(NwdMainCategory, models.DO_NOTHING, blank=True, null=True)
    nwd_subcategory = models.ForeignKey(NwdSubcategory, models.DO_NOTHING, blank=True, null=True)


    def __unicode__(self):
        return "Gtin: " + str(self.gtin)

    class Meta:
        db_table = 'product'


class ProductAttribute(models.Model):
    value = models.TextField(max_length=4000, blank=True, null=True)
    language_code = models.CharField(max_length=255, blank=True, null=True)
    country_code = models.CharField(max_length=255, blank=True, null=True)
    canonical_name = models.TextField(max_length=1024, blank=True, null=True)
    product = models.ForeignKey(Product, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'product_attribute'

class ProductName(models.Model):
    name = models.TextField(max_length=4000, blank=True, null=True)
    language_code = models.CharField(max_length=255, blank=True, null=True)
    country_code = models.CharField(max_length=255, blank=True, null=True)
    product = models.ForeignKey(Product, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'product_name'

class AgreedData(models.Model):
    value = models.TextField(max_length=1024, blank=True, null=True)
    agreed_id = models.CharField(max_length=255, blank=True, null=True)
    product = models.ForeignKey(Product, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'agreed_data'

class MissingTrustboxItem(models.Model):
    name = models.CharField(max_length=255, verbose_name="Name")
    total_weight = models.FloatField(verbose_name="Gesamtgewicht")
    gtin = models.BigIntegerField(verbose_name="GTIN")
    nwd_subcategory = models.ForeignKey(NwdSubcategory, models.DO_NOTHING, blank=True, null=True, verbose_name="Kategorie")
    serving_size = models.FloatField(verbose_name="Serving Size")
    image_url = models.URLField(blank=True, null=True)
    salt = models.FloatField(verbose_name="Salz")
    sodium = models.FloatField(verbose_name="Natrium")
    energy = models.FloatField(verbose_name="Energie")
    fat = models.FloatField(verbose_name="Fett")
    saturated_fat = models.FloatField(verbose_name="Gesaetigtes Fett")
    carbohydrate = models.FloatField(verbose_name="Kohlenhydrate")
    sugar = models.FloatField(verbose_name="davon Zucker")
    fibers = models.FloatField(verbose_name="Ballaststoffe")
    protein = models.FloatField(verbose_name="Protein")

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'missing_trustbox_item'


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)