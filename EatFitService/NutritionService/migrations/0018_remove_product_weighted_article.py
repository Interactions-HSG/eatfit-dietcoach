# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-11-03 15:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('NutritionService', '0017_product_weighted_article'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='weighted_article',
        ),
    ]