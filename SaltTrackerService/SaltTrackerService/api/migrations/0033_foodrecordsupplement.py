# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-08-17 13:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0032_auto_20160817_1316'),
    ]

    operations = [
        migrations.CreateModel(
            name='FoodRecordSupplement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_salt', models.FloatField()),
                ('food_item_supplement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.FoodItemSupplement')),
                ('food_record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.FoodRecord')),
            ],
            options={
                'db_table': 'food_record_supplement',
                'managed': True,
            },
        ),
    ]