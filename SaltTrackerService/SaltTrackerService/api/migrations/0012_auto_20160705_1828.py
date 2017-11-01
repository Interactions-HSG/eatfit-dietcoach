# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-05 16:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_foodrecord_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='MigrosBasket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(max_length=255)),
                ('date_of_purchase_millis', models.BigIntegerField()),
                ('store', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='api.SaltTrackerUser')),
            ],
            options={
                'db_table': 'migros_basket',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='MigrosBasketItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField()),
                ('price', models.FloatField()),
                ('migros_basket', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='api.MigrosBasket')),
            ],
            options={
                'db_table': 'migros_basket_item',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='MigrosItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('gtin', models.BigIntegerField()),
            ],
            options={
                'db_table': 'migros_item',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ReebateCredentials',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('last_reebate_import', models.DateField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='api.SaltTrackerUser')),
            ],
            options={
                'db_table': 'reebate_credentials',
                'managed': True,
            },
        ),
        migrations.AlterField(
            model_name='foodrecord',
            name='daytime',
            field=models.CharField(choices=[(b'Breakfast', b'Breakfast'), (b'Lunch', b'Lunch'), (b'Snack', b'Snack'), (b'Supper', b'Supper')], max_length=25),
        ),
        migrations.AddField(
            model_name='migrosbasketitem',
            name='migros_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='api.MigrosItem'),
        ),
    ]
