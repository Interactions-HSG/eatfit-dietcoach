# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-11 17:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0062_auto_20171111_1426'),
    ]

    operations = [
        migrations.AddField(
            model_name='salttrackeruser',
            name='food_tracker_user',
            field=models.BooleanField(default=False),
        ),
    ]