# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-11-03 14:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NutritionService', '0016_auto_20180728_1920'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='weighted_article',
            field=models.BooleanField(default=False),
        ),
    ]
