# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-06-22 12:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0055_auto_20170620_1702'),
    ]

    operations = [
        migrations.AddField(
            model_name='fooditemsupplement',
            name='show_in_foodtracker',
            field=models.BooleanField(default=False),
        ),
    ]