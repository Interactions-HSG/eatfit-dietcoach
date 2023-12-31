# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-12-31 17:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0039_autoidscrapermigrosbasket_autoidscrapermigrosbasketitem_autoidscrapermigrositem_lmpcategory_missingt'),
    ]

    operations = [
        migrations.AddField(
            model_name='fooditem',
            name='name_de',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='fooditem',
            name='name_en',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='fooditem',
            name='name_fr',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='fooditem',
            name='name_it',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='fooditem',
            name='tooltip_de',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='fooditem',
            name='tooltip_en',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='fooditem',
            name='tooltip_fr',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='fooditem',
            name='tooltip_it',
            field=models.TextField(blank=True, null=True),
        ),
    ]
