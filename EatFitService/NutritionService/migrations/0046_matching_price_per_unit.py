# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2020-02-07 08:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NutritionService', '0045_auto_20200204_0900'),
    ]

    operations = [
        migrations.AddField(
            model_name='matching',
            name='price_per_unit',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
