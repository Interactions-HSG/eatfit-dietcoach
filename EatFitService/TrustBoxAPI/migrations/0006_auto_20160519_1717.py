# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-19 17:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TrustBoxAPI', '0005_auto_20160519_1711'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agreeddata',
            name='value',
            field=models.TextField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='importlog',
            name='failed_reason',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='lmpcategory',
            name='canonical_name',
            field=models.TextField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='lmpcategory',
            name='description',
            field=models.TextField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='nutritionattribute',
            name='canonical_name',
            field=models.TextField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='nutritionfact',
            name='canonical_name',
            field=models.TextField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='nutritionfact',
            name='combined_amount_and_measure',
            field=models.TextField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='nutritiongroupattribute',
            name='canonical_name',
            field=models.TextField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='nutritionlabel',
            name='value',
            field=models.TextField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='nwdmaincategory',
            name='canonical_name',
            field=models.TextField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='nwdmaincategory',
            name='description',
            field=models.TextField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='nwdmaincategoryminnutritionfactdifference',
            name='nutrition_fact_canonical_name',
            field=models.TextField(max_length=1024),
        ),
        migrations.AlterField(
            model_name='nwdsubcategory',
            name='description',
            field=models.TextField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='productattribute',
            name='canonical_name',
            field=models.TextField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='productattribute',
            name='value',
            field=models.TextField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='productname',
            name='name',
            field=models.TextField(blank=True, max_length=1024, null=True),
        ),
    ]