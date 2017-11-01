# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-19 07:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_fooditem_kalium'),
    ]

    operations = [
        migrations.AddField(
            model_name='migrositem',
            name='quantity',
            field=models.FloatField(blank=True, null=True, verbose_name=b'Menge'),
        ),
        migrations.AlterField(
            model_name='migrositem',
            name='price',
            field=models.FloatField(blank=True, null=True, verbose_name=b'Preis in CHF'),
        ),
    ]
