from django.db import models
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
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
    icon = models.ImageField(upload_to ="minor_category_icons", null=True, blank=True, verbose_name="Icon")

    def __unicode__(self):
        return self.description

    class Meta:
        db_table = 'minor_category'


class Product(models.Model):
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
    image = models.ImageField(upload_to ="product_images", null=True, blank=True)
    original_image_url = models.TextField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        db_table = 'product'

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


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)