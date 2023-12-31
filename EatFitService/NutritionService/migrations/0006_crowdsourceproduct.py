# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-05-15 16:51
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('NutritionService', '0005_auto_20180515_1432'),
    ]

    operations = [
        migrations.CreateModel(
            name='CrowdsourceProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('gtin', models.BigIntegerField(unique=True, verbose_name='GTIN')),
                ('product_name_en', models.TextField(blank=True, null=True)),
                ('product_name_de', models.TextField(blank=True, null=True)),
                ('product_name_fr', models.TextField(blank=True, null=True)),
                ('product_name_it', models.TextField(blank=True, null=True)),
                ('producer', models.TextField(blank=True, null=True)),
                ('product_size', models.CharField(blank=True, max_length=255, null=True)),
                ('product_size_unit_of_measure', models.CharField(blank=True, max_length=255, null=True)),
                ('serving_size', models.CharField(blank=True, max_length=255, null=True, verbose_name='Serving Size')),
                ('comment', models.TextField(blank=True, null=True)),
                ('front_image', models.ImageField(blank=True, null=True, upload_to='crowdsoure_images')),
                ('back_image', models.ImageField(blank=True, null=True, upload_to='crowdsoure_images')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('health_percentage', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)], verbose_name='Fruit, Vegetable, Nuts Share')),
                ('salt', models.FloatField(blank=True, null=True, verbose_name='Salz pro 100g/ml in Gramm')),
                ('sodium', models.FloatField(blank=True, null=True, verbose_name='Natrium pro 100g/ml in Gramm')),
                ('energy', models.FloatField(blank=True, null=True, verbose_name='Energie pro 100g/ml in KJ')),
                ('fat', models.FloatField(blank=True, null=True, verbose_name='Fett pro 100g/ml in Gramm')),
                ('saturated_fat', models.FloatField(blank=True, null=True, verbose_name='Ges\xc3\xa4ttigtes Fett pro 100g/ml in Gramm')),
                ('carbohydrate', models.FloatField(blank=True, null=True, verbose_name='Kohlenhydrate pro 100g/ml in Gramm')),
                ('sugar', models.FloatField(blank=True, null=True, verbose_name='davon Zucker pro 100g/ml in Gramm')),
                ('fibers', models.FloatField(blank=True, null=True, verbose_name='Ballaststoffe pro 100g/ml in Gramm')),
                ('protein', models.FloatField(blank=True, null=True, verbose_name='Protein pro 100g/ml in Gramm')),
                ('major_category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='NutritionService.MajorCategory')),
                ('minor_category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='NutritionService.MinorCategory')),
            ],
            options={
                'db_table': 'crowdsource_product',
                'verbose_name': 'Crowdsource Product',
                'verbose_name_plural': 'Crowdsource Products',
            },
        ),
    ]
