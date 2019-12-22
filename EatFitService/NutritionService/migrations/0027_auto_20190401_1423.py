# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-04-01 14:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NutritionService', '0026_auto_20190401_1411'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='allergen',
            name='certainity',
        ),
        migrations.AddField(
            model_name='allergen',
            name='certainty',
            field=models.CharField(choices=[('true', 'true'), ('false', 'false'), ('mayContain', 'mayContain')], default='false', max_length=11),
        ),
    ]
