# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-11 19:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_auto_20160706_1640'),
    ]

    operations = [
        migrations.AddField(
            model_name='migrositem',
            name='price',
            field=models.FloatField(blank=True, null=True),
        ),
    ]