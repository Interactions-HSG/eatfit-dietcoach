# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-09-19 07:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NutritionService', '0033_auto_20190820_0913'),
    ]

    operations = [
        migrations.AddField(
            model_name='minorcategory',
            name='nutri_score_category',
            field=models.CharField(blank=True, choices=[(1, b'Mineral Water'), (2, b'Beverage'), (3, b'Cheese'), (4, b'Added Fat'), (5, b'Food'), (6, b'No Food'), (7, b'Unknown')], max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='nutri_score_by_manufacturer',
            field=models.CharField(blank=True, choices=[(b'A', b'A'), (b'B', b'B'), (b'C', b'C'), (b'D', b'D'), (b'E', b'E')], max_length=1, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='nutri_score_calculated',
            field=models.CharField(blank=True, choices=[(b'A', b'A'), (b'B', b'B'), (b'C', b'C'), (b'D', b'D'), (b'E', b'E')], max_length=1, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='nutri_score_calculated_mixed',
            field=models.CharField(blank=True, choices=[(b'A', b'A'), (b'B', b'B'), (b'C', b'C'), (b'D', b'D'), (b'E', b'E')], max_length=1, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='nutri_score_category_estimated',
            field=models.CharField(blank=True, choices=[(1, b'Mineral Water'), (2, b'Beverage'), (3, b'Cheese'), (4, b'Added Fat'), (5, b'Food'), (6, b'No Food'), (7, b'Unknown')], max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='nutri_score_final',
            field=models.CharField(blank=True, choices=[(b'A', b'A'), (b'B', b'B'), (b'C', b'C'), (b'D', b'D'), (b'E', b'E')], max_length=1, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='nutri_score_quality_comment',
            field=models.TextField(blank=True, choices=[(b'A', b'A'), (b'B', b'B'), (b'C', b'C'), (b'D', b'D'), (b'E', b'E')], null=True),
        ),
    ]
