# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-09-06 11:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0034_auto_20160817_1534'),
    ]

    operations = [
        migrations.AddField(
            model_name='fooditem',
            name='reference_portion',
            field=models.FloatField(blank=True, null=True, verbose_name=b'Portion in g'),
        ),
        migrations.AddField(
            model_name='fooditem',
            name='sodium',
            field=models.FloatField(blank=True, null=True, verbose_name=b'Natrium mg pro 100g'),
        ),
        migrations.AlterField(
            model_name='fooditem',
            name='kalium',
            field=models.FloatField(blank=True, null=True, verbose_name=b'Kalium mg pro 100g'),
        ),
    ]