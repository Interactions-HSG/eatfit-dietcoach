# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-05-30 15:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0046_auto_20170422_1751'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fooditem',
            options={'managed': True, 'ordering': ['sort']},
        ),
        migrations.AddField(
            model_name='fooditem',
            name='sort',
            field=models.PositiveIntegerField(db_index=True, default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='profiledata',
            name='profile_data_type',
            field=models.CharField(choices=[(b'House_Hold_Data', b'House_Hold_Data'), (b'Eating_Habits_Data', b'Eating_Habits_Data'), (b'Shopping_Habits_Data', b'Shopping_Habits_Data'), (b'General', b'General'), (b'Food_Tracker', b'Food_Tracker'), (b'Salt_Tracker', b'Salt_Tracker'), (b'Analysis_Survey', b'Analysis_Survey')], max_length=255),
        ),
    ]