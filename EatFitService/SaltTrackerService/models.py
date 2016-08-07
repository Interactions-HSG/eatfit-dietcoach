# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class SaltTrackerUser(models.Model):
    user = models.OneToOneField(User, models.CASCADE, primary_key=True)
    nickname = models.CharField(unique=True, max_length=50)
    profile_image = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=80, blank=True, null=True)
    zip = models.CharField(max_length=15, blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    sex = models.CharField(max_length=15, blank=True, null=True)
    notification_id = models.CharField(max_length=100, blank=True, null=True)
    operating_system = models.CharField(max_length=20, blank=True, null=True)
    cumulus_email = models.CharField(max_length=254, blank=True, null=True)
    cumulus_password = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'salt_tracker_user'

class ReebateCredentials(models.Model):
    user = models.ForeignKey(SaltTrackerUser, models.DO_NOTHING)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    last_reebate_import = models.BigIntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'reebate_credentials'

class MigrosBasket(models.Model):
    user = models.ForeignKey(SaltTrackerUser, models.DO_NOTHING)
    external_id = models.CharField(max_length=255)
    date_of_purchase_millis = models.BigIntegerField()
    store = models.CharField(max_length=255)
    added_date = models.DateTimeField(blank=True)

    class Meta:
        managed = False
        db_table = 'migros_basket'

class MigrosItem(models.Model):
    name = models.CharField(max_length=255)
    gtin = models.BigIntegerField(null=True, blank=True)
    price = models.FloatField()
    quantity = models.FloatField(null=True, blank=True, verbose_name="Menge")

    class Meta:
        managed = False
        db_table = 'migros_item'

class MigrosBasketItem(models.Model):
    migros_basket = models.ForeignKey(MigrosBasket, models.CASCADE)
    migros_item = models.ForeignKey(MigrosItem, models.DO_NOTHING)
    quantity = models.FloatField()
    price = models.FloatField()

    class Meta:
        managed = False
        db_table = 'migros_basket_item'

class ShoppingResult(models.Model):
    gtin  = models.BigIntegerField()
    purchased = models.DateTimeField()
    total_salt = models.FloatField()
    total_fat = models.FloatField()
    total_sugar = models.FloatField()
    serving_size = models.FloatField()
    quantity = models.FloatField()
    user = models.ForeignKey(User)
    added = models.DateTimeField()
    nwd_subcategory_name = models.TextField(max_length=1024, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'shopping_result'

class ShoppingTip(models.Model):
    text = models.TextField(verbose_name="Text")
    nwd_subcategory_name = models.TextField(max_length=1024, blank=True, null=True, verbose_name="(Sub-)Kategoriename")
    category_color = models.CharField(max_length=255, verbose_name="Kategoriefarbe")
    is_general = models.BooleanField(default=False, verbose_name="Allgemeiner Tipp")
    icon = models.ImageField(upload_to ="shopping_tips",null=True, blank=True, verbose_name="Icon")

    def __unicode__(self):
        return self.text[:20]

    class Meta:
        managed = True
        db_table = 'shopping_tip'
        app_label = 'api' 

