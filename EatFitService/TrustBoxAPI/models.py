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


class ImportLog(models.Model):
    import_timestamp = models.DateTimeField()
    successful = models.BooleanField()
    failed_reason = models.TextField(max_length=500, blank=True, null=True)
    product_gtin = models.TextField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = 'import_log'
        app_label = 'trustbox_api' 

class LmpCategory(models.Model):
    lmp_id = models.IntegerField(primary_key=True)
    description = models.TextField(max_length=1024, blank=True, null=True)
    canonical_name = models.TextField(max_length=1024, blank=True, null=True)

    class Meta:
        db_table = 'lmp_category'
        app_label = 'trustbox_api' 


class Nutrition(models.Model):
    product = models.OneToOneField('Product', primary_key=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'nutrition'
        app_label = 'trustbox_api' 


class NutritionAttribute(models.Model):
    value = models.CharField(max_length=4000, blank=True, null=True)
    language_code = models.CharField(max_length=255, blank=True, null=True)
    country_code = models.CharField(max_length=255, blank=True, null=True)
    canonical_name = models.TextField(max_length=4000, blank=True, null=True)
    nutrition = models.ForeignKey(Nutrition, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'nutrition_attribute'
        app_label = 'trustbox_api' 


class NutritionFact(models.Model):
    amount = models.CharField(max_length=255, blank=True, null=True)
    unit_of_measure = models.CharField(max_length=255, blank=True, null=True)
    combined_amount_and_measure = models.TextField(max_length=1024, blank=True, null=True)
    daily_percent = models.CharField(max_length=255, blank=True, null=True)
    language_code = models.CharField(max_length=255, blank=True, null=True)
    country_code = models.CharField(max_length=255, blank=True, null=True)
    canonical_name = models.TextField(max_length=4000, blank=True, null=True)
    nutrition_facts_group = models.ForeignKey('NutritionFactsGroup', on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'nutrition_fact'
        app_label = 'trustbox_api' 


class NutritionFactsGroup(models.Model):
    nutrition = models.OneToOneField('Nutrition', primary_key=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'nutrition_facts_group'
        app_label = 'trustbox_api' 


class NutritionGroupAttribute(models.Model):
    value = models.CharField(max_length=4000, blank=True, null=True)
    language_code = models.CharField(max_length=255, blank=True, null=True)
    country_code = models.CharField(max_length=255, blank=True, null=True)
    canonical_name = models.TextField(max_length=1024, blank=True, null=True)
    nutrition_facts_group = models.ForeignKey(NutritionFactsGroup, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'nutrition_group_attribute'
        app_label = 'trustbox_api' 


class NutritionLabel(models.Model):
    value = models.TextField(max_length=4000, blank=True, null=True)
    label_id = models.IntegerField(blank=True, null=True)
    nutrition = models.ForeignKey(Nutrition, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'nutrition_label'
        app_label = 'trustbox_api' 


class NwdMainCategory(models.Model):
    nwd_main_category_id = models.IntegerField(primary_key=True)
    description = models.TextField(max_length=1024, blank=True, null=True)
    canonical_name = models.TextField(max_length=1024, blank=True, null=True)

    class Meta:
        db_table = 'nwd_main_category'
        app_label = 'trustbox_api' 


class NwdMainCategoryMinNutritionFactDifference(models.Model):
    min_absolute = models.FloatField(blank=True, null=True)
    min_relative = models.IntegerField(blank=True, null=True)
    nutrition_fact_canonical_name = models.TextField(max_length=1024)
    nwd_main_category = models.ForeignKey(NwdMainCategory, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'nwd_main_category_min_nutrition_fact_difference'
        app_label = 'trustbox_api' 


class NwdSubcategory(models.Model):
    nwd_subcategory_id = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(max_length=1024, blank=True, null=True)
    nwd_main_category = models.ForeignKey(NwdMainCategory, on_delete=models.DO_NOTHING, blank=True, null=True)
    lmp = models.ForeignKey(LmpCategory, on_delete=models.DO_NOTHING, blank=True, null=True)
    icon = models.ImageField(upload_to ="subcategory_icons",null=True, blank=True, verbose_name="Icon")

    def __str__(self):
        return self.description

    class Meta:
        db_table = 'nwd_subcategory'
        app_label = 'trustbox_api' 


class NwdSubcategoryMinNutritionFactDifference(models.Model):
    min_absolute = models.FloatField(blank=True, null=True)
    min_relative = models.IntegerField(blank=True, null=True)
    nutrition_fact_canonical_name = models.CharField(max_length=255)
    nwd_subcategory = models.ForeignKey(NwdSubcategory, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'nwd_subcategory_min_nutrition_fact_difference'
        app_label = 'trustbox_api' 


class Product(models.Model):
    target_market_country_code = models.SmallIntegerField(blank=True, null=True)
    gln = models.BigIntegerField(blank=True, null=True)
    gtin = models.BigIntegerField()
    status = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.CharField(max_length=255, blank=True, null=True)
    nwd_main_category = models.ForeignKey(NwdMainCategory, on_delete=models.DO_NOTHING, blank=True, null=True)
    nwd_subcategory = models.ForeignKey(NwdSubcategory, on_delete=models.DO_NOTHING, blank=True, null=True)


    def __str__(self):
        return "Gtin: " + str(self.gtin)

    class Meta:
        db_table = 'product'
        app_label = 'trustbox_api' 


class ProductAttribute(models.Model):
    value = models.TextField(max_length=4000, blank=True, null=True)
    language_code = models.CharField(max_length=255, blank=True, null=True)
    country_code = models.CharField(max_length=255, blank=True, null=True)
    canonical_name = models.TextField(max_length=1024, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'product_attribute'
        app_label = 'trustbox_api' 

class ProductName(models.Model):
    name = models.TextField(max_length=4000, blank=True, null=True)
    language_code = models.CharField(max_length=255, blank=True, null=True)
    country_code = models.CharField(max_length=255, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'product_name'
        app_label = 'trustbox_api' 

class AgreedData(models.Model):
    value = models.TextField(max_length=1024, blank=True, null=True)
    agreed_id = models.CharField(max_length=255, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'agreed_data'
        app_label = 'trustbox_api' 

class MissingTrustboxItem(models.Model):
    name = models.CharField(max_length=255, verbose_name="Name")
    total_weight = models.FloatField(verbose_name="Gesamtgewicht in Gramm")
    gtin = models.BigIntegerField(verbose_name="GTIN")
    nwd_subcategory = models.ForeignKey(NwdSubcategory, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name="Kategorie")
    serving_size = models.FloatField(verbose_name="Serving Size")
    image_url = models.URLField(blank=True, null=True)
    salt = models.FloatField(verbose_name="Salz pro 100g/ml in Gramm")
    sodium = models.FloatField(verbose_name="Natrium pro 100g/ml in Gramm")
    energy = models.FloatField(verbose_name="Energie pro 100g/ml in KJ")
    fat = models.FloatField(verbose_name="Fett pro 100g/ml in Gramm")
    saturated_fat = models.FloatField(verbose_name="Gesättigtes Fett pro 100g/ml in Gramm")
    carbohydrate = models.FloatField(verbose_name="Kohlenhydrate pro 100g/ml in Gramm")
    sugar = models.FloatField(verbose_name="davon Zucker pro 100g/ml in Gramm")
    fibers = models.FloatField(verbose_name="Ballaststoffe pro 100g/ml in Gramm")
    protein = models.FloatField(verbose_name="Protein pro 100g/ml in Gramm")
    price = models.FloatField(verbose_name="Preis in CHF", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'missing_trustbox_item'
        app_label = 'trustbox_api' 
