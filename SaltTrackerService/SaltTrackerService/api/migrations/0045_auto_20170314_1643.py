# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-03-14 16:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0044_auto_20170113_1707'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foodrecord',
            name='daytime',
            field=models.CharField(choices=[(b'Breakfast', b'Breakfast'), (b'Lunch', b'Lunch'), (b'Snack', b'Snack'), (b'Supper', b'Supper'), (b'MorningSnack', b'MorningSnack'), (b'AfternoonSnack', b'AfternoonSnack'), (b'MidnightSnack', b'MidnightSnack')], max_length=25),
        ),
        migrations.AlterField(
            model_name='profiledata',
            name='profile_data_type',
            field=models.CharField(choices=[(b'House_Hold_Data', b'House_Hold_Data'), (b'Eating_Habits_Data', b'Eating_Habits_Data'), (b'Shopping_Habits_Data', b'Shopping_Habits_Data'), (b'General', b'General'), (b'Analysis_Survey', b'Analysis_Survey')], max_length=255),
        ),
    ]
