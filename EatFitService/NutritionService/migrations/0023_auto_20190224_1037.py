# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-02-24 10:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NutritionService', '0022_auto_20190110_1029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nonfoundmatching',
            name='counter',
            field=models.IntegerField(default=0),
        ),
    ]
