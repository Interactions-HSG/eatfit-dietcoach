# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-09-26 13:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NutritionService', '0034_auto_20190919_0700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='minorcategory',
            name='nutri_score_category',
            field=models.CharField(blank=True, choices=[(b'Mineral Water', b'Mineral Water'), (b'Beverage', b'Beverage'), (b'Cheese', b'Cheese'), (b'Added Fat', b'Added Fat'), (b'Food', b'Food'), (b'No Food', b'No Food'), (b'Unknown', b'Unknown')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='nutri_score_category_estimated',
            field=models.CharField(blank=True, choices=[(b'Mineral Water', b'Mineral Water'), (b'Beverage', b'Beverage'), (b'Cheese', b'Cheese'), (b'Added Fat', b'Added Fat'), (b'Food', b'Food'), (b'No Food', b'No Food'), (b'Unknown', b'Unknown')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='nutri_score_quality_comment',
            field=models.TextField(blank=True, null=True),
        ),
    ]
