# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-22 17:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TrustBoxAPI', '0008_auto_20160521_2052'),
    ]

    operations = [
        migrations.AddField(
            model_name='importlog',
            name='product_gtin',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
    ]