# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-09-06 13:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0035_auto_20160906_1342'),
    ]

    operations = [
        migrations.AddField(
            model_name='fooditemsupplement',
            name='reference_portion',
            field=models.FloatField(blank=True, null=True, verbose_name=b'Portion in g'),
        ),
        migrations.AddField(
            model_name='fooditemsupplement',
            name='sodium',
            field=models.FloatField(blank=True, null=True, verbose_name=b'Natrium mg pro 100g'),
        ),
        migrations.AlterField(
            model_name='fooditemsupplement',
            name='kalium',
            field=models.FloatField(blank=True, null=True, verbose_name=b'Kalium mg pro 100g'),
        ),
    ]
