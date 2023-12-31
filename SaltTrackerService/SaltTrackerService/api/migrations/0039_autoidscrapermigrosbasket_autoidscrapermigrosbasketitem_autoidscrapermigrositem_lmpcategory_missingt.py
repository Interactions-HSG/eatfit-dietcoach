# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-12-31 17:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0038_auto_20160920_2211'),
    ]

    operations = [
        migrations.CreateModel(
            name='AutoidScraperMigrosBasket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('storename', models.CharField(blank=True, max_length=255, null=True)),
                ('transaction_nr', models.FloatField(blank=True, null=True)),
                ('kst', models.IntegerField(blank=True, null=True)),
                ('knr', models.IntegerField(blank=True, null=True)),
                ('purchase_datetime', models.DateTimeField(blank=True, null=True)),
                ('total_price', models.FloatField(blank=True, null=True)),
                ('url', models.TextField(blank=True, null=True)),
                ('added_datetime', models.DateTimeField(blank=True, null=True)),
                ('received_points', models.FloatField(blank=True, null=True)),
                ('generated_id', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'autoid_scraper_migros_basket',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AutoidScraperMigrosBasketItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField(blank=True, null=True)),
                ('price', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'autoid_scraper_migros_basket_item',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AutoidScraperMigrosItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(blank=True, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('gtin', models.BigIntegerField(blank=True, null=True)),
                ('avg_price', models.FloatField(blank=True, null=True)),
                ('total_quantity', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'autoid_scraper_migros_item',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LmpCategory',
            fields=[
                ('lmp_id', models.IntegerField(primary_key=True, serialize=False)),
                ('description', models.TextField(blank=True, max_length=1024, null=True)),
                ('canonical_name', models.TextField(blank=True, max_length=1024, null=True)),
            ],
            options={
                'db_table': 'lmp_category',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MissingTrustboxItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name=b'Name')),
                ('total_weight', models.FloatField(verbose_name=b'Gesamtgewicht in Gramm')),
                ('gtin', models.BigIntegerField(verbose_name=b'GTIN')),
                ('serving_size', models.FloatField(verbose_name=b'Serving Size')),
                ('image_url', models.URLField(blank=True, null=True)),
                ('salt', models.FloatField(verbose_name=b'Salz pro 100g/ml in Gramm')),
                ('sodium', models.FloatField(verbose_name=b'Natrium pro 100g/ml in Gramm')),
                ('energy', models.FloatField(verbose_name=b'Energie pro 100g/ml in KJ')),
                ('fat', models.FloatField(verbose_name=b'Fett pro 100g/ml in Gramm')),
                ('saturated_fat', models.FloatField(verbose_name=b'Ges\xc3\xa4ttigtes Fett pro 100g/ml in Gramm')),
                ('carbohydrate', models.FloatField(verbose_name=b'Kohlenhydrate pro 100g/ml in Gramm')),
                ('sugar', models.FloatField(verbose_name=b'davon Zucker pro 100g/ml in Gramm')),
                ('fibers', models.FloatField(verbose_name=b'Ballaststoffe pro 100g/ml in Gramm')),
                ('protein', models.FloatField(verbose_name=b'Protein pro 100g/ml in Gramm')),
                ('price', models.FloatField(blank=True, null=True, verbose_name=b'Preis in CHF')),
            ],
            options={
                'db_table': 'missing_trustbox_item',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='NwdMainCategory',
            fields=[
                ('nwd_main_category_id', models.IntegerField(primary_key=True, serialize=False)),
                ('description', models.TextField(blank=True, max_length=1024, null=True)),
                ('canonical_name', models.TextField(blank=True, max_length=1024, null=True)),
            ],
            options={
                'db_table': 'nwd_main_category',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='NwdSubcategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nwd_subcategory_id', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, max_length=1024, null=True)),
                ('icon', models.ImageField(blank=True, null=True, upload_to=b'subcategory_icons', verbose_name=b'Icon')),
            ],
            options={
                'db_table': 'nwd_subcategory',
                'managed': False,
            },
        ),
    ]
