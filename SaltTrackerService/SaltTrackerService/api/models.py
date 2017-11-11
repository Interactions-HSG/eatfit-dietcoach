"""
Definition of models.
"""

from django.db import models
from adminsortable.models import SortableMixin
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.dispatch.dispatcher import receiver
from django.conf import settings
from django.db.models.signals import post_save
from datetime import datetime

class SaltTrackerUser(models.Model):
    MALE = "Male"
    FEMALE = "Female"
    TRANSGENDER = "Transgender"
    SEX_CHOICES = (
        (MALE, "Male"),
        (FEMALE, "Female"),
        (TRANSGENDER, "Transgender")
    )

    IOS = "iOS"
    ANDROID = "Android"
    WIN10 = "Win10"
    OS_CHOICES = (
        (IOS, "iOS"),
        (ANDROID, "Android"),
        (WIN10, "Win10")
    )

    user = models.OneToOneField(User, primary_key=True)
    nickname = models.CharField(max_length=50)
    profile_image = models.ImageField(blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    country =  models.CharField(max_length=80, null=True, blank=True)
    zip = models.CharField(max_length=15, null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    sex = models.CharField(max_length=15, null=True, choices=SEX_CHOICES, blank=True)
    notification_id = models.CharField(null=True, blank=True, max_length=100)
    operating_system = models.CharField(max_length=20, null=True, blank=True, choices = OS_CHOICES)
    cumulus_email = models.EmailField(null=True, blank=True)
    cumulus_password = models.CharField(max_length=255, null=True, blank=True)
    
    def __unicode__(self):
        return self.user.email

    class Meta:
        managed = True
        db_table = 'salt_tracker_user'
        app_label = 'api' 

class ReebateCredentials(models.Model):
    user = models.ForeignKey(SaltTrackerUser, models.DO_NOTHING)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    last_reebate_import = models.BigIntegerField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'reebate_credentials'
        app_label = 'api' 

class MigrosBasket(models.Model):
    user = models.ForeignKey(SaltTrackerUser, models.DO_NOTHING)
    external_id = models.CharField(max_length=255)
    date_of_purchase_millis = models.BigIntegerField()
    store = models.CharField(max_length=255)
    added_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'migros_basket'
        app_label = 'api' 

class MigrosItem(models.Model):
    name = models.CharField(max_length=255)
    gtin = models.BigIntegerField(null=True, blank=True)
    price = models.FloatField(null=True, blank=True, verbose_name="Preis in CHF")
    quantity = models.FloatField(null=True, blank=True, verbose_name="Menge")

    class Meta:
        managed = True
        db_table = 'migros_item'
        app_label = 'api' 

class MigrosBasketItem(models.Model):
    migros_basket = models.ForeignKey(MigrosBasket, models.DO_NOTHING)
    migros_item = models.ForeignKey(MigrosItem, models.DO_NOTHING)
    quantity = models.FloatField()
    price = models.FloatField()

    class Meta:
        managed = True
        db_table = 'migros_basket_item'
        app_label = 'api' 

class ShoppingResult(models.Model):
    gtin  = models.BigIntegerField()
    purchased = models.DateTimeField()
    total_salt = models.FloatField()
    total_fat = models.FloatField(default=0)
    total_sugar = models.FloatField(default = 0)
    serving_size = models.FloatField(default = 0)
    quantity = models.FloatField()
    user = models.ForeignKey(User)
    added = models.DateTimeField()
    nwd_subcategory_name = models.TextField(max_length=1024, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'shopping_result'
        app_label = 'api' 

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

class Study(models.Model):
    start_date = models.DateTimeField(default=datetime.now, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_successful = models.BooleanField(default=False)
    is_lost = models.BooleanField(default=False)
    survey_completed = models.BooleanField(default=False)
    weeks = models.IntegerField(default=2)
    min_records_per_week = models.IntegerField(default=4)
    user = models.ForeignKey(User, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'study'
        app_label = 'api' 

class StudyDay(models.Model):
    date = models.DateTimeField(default=datetime.now, blank=True)
    is_locked = models.BooleanField(default=True)
    study = models.ForeignKey("Study")
    user = models.ForeignKey(User, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'study_day'
        app_label = 'api' 

class Category(SortableMixin):
    name = models.CharField(max_length=255)
    category_detail_text = models.CharField(max_length=255, null=True, blank=True)
    category_color = models.CharField(max_length=255)
    category_icon = models.ImageField(upload_to ="category_icons", null=True, blank=True, verbose_name="Icon")
    sort = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'category'
        app_label = 'api' 
        ordering = ['sort']



class FoodItem(SortableMixin):
    name = models.CharField(max_length=255)
    icon = models.ImageField(null=True, blank=True)
    unit = models.CharField(max_length=255)
    salt = models.FloatField()
    sodium = models.FloatField(null=True, blank=True, verbose_name="Natrium mg pro 100g")
    kalium = models.FloatField(null=True, blank=True, verbose_name="Kalium mg pro 100g")
    sugar = models.FloatField(null=True, blank=True)
    added_sugar = models.FloatField(null=True, blank=True)
    fruit = models.FloatField(null=True, blank=True)
    vegetables = models.FloatField(null=True, blank=True)
    alcohol = models.FloatField(null=True, blank=True)
    reference_portion = models.FloatField(null=True, blank=True,verbose_name="Portion in g")
    category = models.ForeignKey("Category")
    tooltip = models.TextField(null=True, blank=True)
    red_cap_id = models.CharField(max_length=255, null=True, blank=True)
    supplements = models.ManyToManyField("FoodItemSupplement", blank=True)
    show_in_foodtracker = models.BooleanField(default=False)
    sort = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'food_item'
        app_label = 'api' 
        ordering = ['sort']


class FoodItemSupplement(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ImageField(null=True, blank=True)
    unit = models.CharField(max_length=255)
    salt = models.FloatField()
    sodium = models.FloatField(null=True, blank=True, verbose_name="Natrium mg pro 100g")
    kalium = models.FloatField(null=True, blank=True, verbose_name="Kalium mg pro 100g")
    sugar = models.FloatField(null=True, blank=True)
    added_sugar = models.FloatField(null=True, blank=True)
    fruit = models.FloatField(null=True, blank=True)
    vegetables = models.FloatField(null=True, blank=True)
    alcohol = models.FloatField(null=True, blank=True)
    reference_portion = models.FloatField(null=True, blank=True,verbose_name="Portion in g")
    red_cap_id = models.CharField(max_length=255, null=True, blank=True)
    show_in_foodtracker = models.BooleanField(default=False)
    category = models.ForeignKey("Category", null=True, blank=True)

    def __unicode__(self):
        if not self.category:
            return self.name
        else:
            return self.name + " in " + self.category.name

    class Meta:
        managed = True
        db_table = 'food_item_supplement'
        app_label = 'api' 

class FoodRecord(models.Model):
    BREAKFAST = "Breakfast"
    LUNCH = "Lunch"
    SNACK = "Snack"
    SUPPER = "Supper"
    MORNING_SNACK = "MorningSnack"
    AFTERNOON_SNACK = "AfternoonSnack"
    MIDNIGHT_SNACK = "MidnightSnack"
    DAYTIME_CHOICES = (
        (BREAKFAST, "Breakfast"),
        (LUNCH, "Lunch"),
        (SNACK, "Snack"),
        (SUPPER, "Supper"),
        (MORNING_SNACK, "MorningSnack"),
        (AFTERNOON_SNACK, "AfternoonSnack"),
        (MIDNIGHT_SNACK, "MidnightSnack"),
    )
    daytime = models.CharField(max_length=25, choices=DAYTIME_CHOICES)
    numberOfPortions = models.FloatField()
    total_salt = models.FloatField()
    total_sugar = models.FloatField(null=True, blank=True)
    total_added_sugar = models.FloatField(null=True, blank=True)
    total_fruit = models.FloatField(null=True, blank=True)
    total_vegetables = models.FloatField(null=True, blank=True)
    total_alcohol = models.FloatField(null=True, blank=True)
    food_item = models.ForeignKey("FoodItem")
    user = models.ForeignKey(User, null=True, blank=True)
    study_day = models.ForeignKey("StudyDay", null=True, blank=True)
    date = models.DateField(blank=True)
    added = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'food_record'
        app_label = 'api' 

class FoodRecordSupplement(models.Model):
    total_salt = models.FloatField()
    total_sugar = models.FloatField(null=True, blank=True)
    total_added_sugar = models.FloatField(null=True, blank=True)
    total_fruit = models.FloatField(null=True, blank=True)
    total_vegetables = models.FloatField(null=True, blank=True)
    total_alcohol = models.FloatField(null=True, blank=True)
    food_item_supplement = models.ForeignKey("FoodItemSupplement")
    food_record = models.ForeignKey("FoodRecord")

    class Meta:
        managed = True
        db_table = 'food_record_supplement'
        app_label = 'api' 

class ProfileData(models.Model):
    HOUSE_HOLD_DATA = "House_Hold_Data"
    EATING_HABITS_DATA = "Eating_Habits_Data"
    SHOPPING_HABITS_DATA = "Shopping_Habits_Data"
    GENERAL = "General"
    SALT_TRACKER = "Salt_Tracker"
    FOOD_TRACKER = "Food_Tracker"
    Analysis_Survey = "Analysis_Survey"
    Nutrition_Avatar = "Nutrition_Avatar"
    
    PROFILE_DATA_TYPE_CHOICES = (
        (HOUSE_HOLD_DATA, "House_Hold_Data"),
        (EATING_HABITS_DATA, "Eating_Habits_Data"),
        (SHOPPING_HABITS_DATA, "Shopping_Habits_Data"),
        (GENERAL, "General"),
        (FOOD_TRACKER, "Food_Tracker"),
        (SALT_TRACKER, "Salt_Tracker"),
        (Analysis_Survey, "Analysis_Survey"),
        (Nutrition_Avatar, "Nutrition_Avatar"),
    )

    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    profile_data_type = models.CharField(max_length=255, choices=PROFILE_DATA_TYPE_CHOICES)
    user = models.ForeignKey(User, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'profile_data'
        app_label = 'api' 


class CustomText(models.Model):
    text = models.TextField()
    weight = models.FloatField()
    added = models.DateTimeField()
    user = models.ForeignKey(User)

    class Meta:
        managed = True
        db_table = 'custom_text'
        app_label = 'api' 


class AutoidScraperMigrosItem(models.Model):
    count = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    gtin = models.BigIntegerField(blank=True, null=True)
    avg_price = models.FloatField(blank=True, null=True)
    total_quantity = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'autoid_scraper_migros_item'

class AutoidScraperMigrosBasket(models.Model):
    user = models.ForeignKey('SaltTrackerUser', models.DO_NOTHING)
    storename = models.CharField(max_length=255, blank=True, null=True)
    transaction_nr = models.FloatField(blank=True, null=True)
    kst = models.IntegerField(blank=True, null=True)
    knr = models.IntegerField(blank=True, null=True)
    purchase_datetime = models.DateTimeField(blank=True, null=True)
    total_price = models.FloatField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)  # This field type is a guess.
    added_datetime = models.DateTimeField(blank=True, null=True)
    received_points = models.FloatField(blank=True, null=True)
    generated_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'autoid_scraper_migros_basket'

class AutoidScraperMigrosBasketItem(models.Model):
    quantity = models.FloatField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    autoid_scraper_migros_basket = models.ForeignKey(AutoidScraperMigrosBasket, models.DO_NOTHING)
    autoid_scraper_migros_item = models.ForeignKey('AutoidScraperMigrosItem', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'autoid_scraper_migros_basket_item'

class AvatarData(models.Model):
    outfit_type = models.CharField(max_length=50, blank=True, null=True)
    head_type = models.CharField(max_length=50, blank=True, null=True)
    eyecolor_type = models.CharField(max_length=50, blank=True, null=True)
    nose_type = models.CharField(max_length=50, blank=True, null=True)
    hair_type = models.CharField(max_length=50, blank=True, null=True)
    glasses_type = models.CharField(max_length=50, blank=True, null=True)
    shoes_type = models.CharField(max_length=50, blank=True, null=True)
    beard_type = models.CharField(max_length=50, blank=True, null=True)
    show_tutorial = models.BooleanField(default = True)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return self.user.username

    class Meta:
        managed = True
        db_table = 'avatar_data'
        app_label = 'api' 

class AvatarMessage(models.Model):
    ingredient = models.CharField(max_length=50)
    ingredient_level = models.IntegerField()
    message = models.CharField(max_length=255)
    sort = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    def __unicode__(self):
        return self.__dict__["message"]

    class Meta:
        managed = True
        db_table = 'avatar_message'
        app_label = 'api'
        ordering = ['sort']

class AvatarTip(models.Model):
    ingredient = models.CharField(max_length=50)
    ingredient_level = models.IntegerField()
    message = models.CharField(max_length=255)

    def __unicode__(self):
        return self.__dict__["message"]

    class Meta:
        managed = True
        db_table = 'avatar_tip'
        app_label = 'api' 

class AvatarLog(models.Model):
    time = models.DateTimeField()
    message = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)
    
    def __unicode__(self):
        return self.message

    class Meta:
        managed = True
        db_table = 'avatar_log'
        app_label = 'api' 


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)



    