# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2020-02-03 11:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NutritionService', '0041_auto_20191011_1031'),
    ]

    operations = [
        migrations.CreateModel(
            name='CurrentStudies',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('study_name', models.CharField(max_length=255)),
                ('study_teaser_de', models.CharField(max_length=255)),
                ('study_teaser_en', models.CharField(max_length=255)),
                ('study_teaser_fr', models.CharField(max_length=255)),
                ('study_teaser_it', models.CharField(max_length=255)),
                ('icon', models.ImageField(upload_to='current_studies_icon')),
                ('banner', models.ImageField(upload_to='current_studies_banner')),
            ],
            options={
                'verbose_name': 'Current Study',
                'verbose_name_plural': 'Current Studies',
                'db_table': 'current_studies',
            },
        ),
        migrations.AlterField(
            model_name='crowdsourceproduct',
            name='saturated_fat',
            field=models.FloatField(blank=True, null=True, verbose_name='Gesättigtes Fett pro 100g/ml in Gramm'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='product_images'),
        ),
    ]
