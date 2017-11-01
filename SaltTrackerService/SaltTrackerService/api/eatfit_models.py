#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

class LmpCategory(models.Model):
    lmp_id = models.IntegerField(primary_key=True)
    description = models.TextField(max_length=1024, blank=True, null=True)
    canonical_name = models.TextField(max_length=1024, blank=True, null=True)

    class Meta:
        managed=False
        db_table = 'lmp_category'

class NwdMainCategory(models.Model):
    nwd_main_category_id = models.IntegerField(primary_key=True)
    description = models.TextField(max_length=1024, blank=True, null=True)
    canonical_name = models.TextField(max_length=1024, blank=True, null=True)

    class Meta:
        managed=False
        db_table = 'nwd_main_category'

class NwdSubcategory(models.Model):
    nwd_subcategory_id = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(max_length=1024, blank=True, null=True)
    nwd_main_category = models.ForeignKey(NwdMainCategory, models.DO_NOTHING, blank=True, null=True)
    lmp = models.ForeignKey(LmpCategory, models.DO_NOTHING, blank=True, null=True)
    icon = models.ImageField(upload_to ="subcategory_icons",null=True, blank=True, verbose_name="Icon")

    def __unicode__(self):
        return self.description

    class Meta:
        managed=False
        db_table = 'nwd_subcategory'

class MissingTrustboxItem(models.Model):
    name = models.CharField(max_length=255, verbose_name="Name")
    total_weight = models.FloatField(verbose_name="Gesamtgewicht in Gramm")
    gtin = models.BigIntegerField(verbose_name="GTIN")
    nwd_subcategory = models.ForeignKey(NwdSubcategory, models.DO_NOTHING, blank=True, null=True, verbose_name="Kategorie")
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

    def __unicode__(self):
        return self.name

    class Meta:
        managed=False
        db_table = 'missing_trustbox_item'
