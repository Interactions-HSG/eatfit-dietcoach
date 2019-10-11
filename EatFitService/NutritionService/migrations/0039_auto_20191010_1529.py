# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-10-10 15:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('NutritionService', '0038_product_nutri_score_number_of_errors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='found_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='product',
            name='major_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='NutritionService.MajorCategory'),
        ),
        migrations.AlterField(
            model_name='product',
            name='ofcom_value',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
