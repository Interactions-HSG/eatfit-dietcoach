# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-11-18 17:52
from __future__ import unicode_literals

import NutritionService.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('NutritionService', '0020_auto_20181110_1816'),
    ]

    operations = [
        migrations.AddField(
            model_name='matching',
            name='eatfit_product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='NutritionService.Product'),
        ),
        migrations.AlterField(
            model_name='crowdsourceproduct',
            name='back_image',
            field=models.ImageField(blank=True, null=True, upload_to=NutritionService.models.path_and_rename),
        ),
        migrations.AlterField(
            model_name='crowdsourceproduct',
            name='front_image',
            field=models.ImageField(blank=True, null=True, upload_to=NutritionService.models.path_and_rename),
        ),
        migrations.AlterField(
            model_name='matching',
            name='gtin',
            field=models.BigIntegerField(),
        ),
    ]
