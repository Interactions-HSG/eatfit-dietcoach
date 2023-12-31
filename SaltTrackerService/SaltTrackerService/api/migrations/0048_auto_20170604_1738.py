# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-06-04 17:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0047_auto_20170530_1545'),
    ]

    operations = [
        migrations.AddField(
            model_name='fooditem',
            name='added_sugar',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='fooditem',
            name='alcohol',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='fooditem',
            name='fruit',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='fooditem',
            name='show_in_foodtracker',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='fooditem',
            name='sugar',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='fooditem',
            name='vegetables',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
