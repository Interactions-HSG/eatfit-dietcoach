# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-08-14 12:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NutritionService', '0031_auto_20190509_1550'),
    ]

    operations = [
        migrations.AddField(
            model_name='nutritionfact',
            name='is_mixed',
            field=models.BooleanField(default=False),
        ),
    ]
