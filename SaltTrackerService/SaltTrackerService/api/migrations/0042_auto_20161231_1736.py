# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-12-31 17:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0041_auto_20161231_1731'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='name_de',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_en',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_fr',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_it',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='fooditemsupplement',
            name='name_de',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='fooditemsupplement',
            name='name_en',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='fooditemsupplement',
            name='name_fr',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='fooditemsupplement',
            name='name_it',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='fooditemsupplement',
            name='unit_de',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='fooditemsupplement',
            name='unit_en',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='fooditemsupplement',
            name='unit_fr',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='fooditemsupplement',
            name='unit_it',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='shoppingtip',
            name='text_de',
            field=models.TextField(null=True, verbose_name=b'Text'),
        ),
        migrations.AddField(
            model_name='shoppingtip',
            name='text_en',
            field=models.TextField(null=True, verbose_name=b'Text'),
        ),
        migrations.AddField(
            model_name='shoppingtip',
            name='text_fr',
            field=models.TextField(null=True, verbose_name=b'Text'),
        ),
        migrations.AddField(
            model_name='shoppingtip',
            name='text_it',
            field=models.TextField(null=True, verbose_name=b'Text'),
        ),
    ]
