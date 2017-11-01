# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-06-20 17:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0054_avatardata_show_tutorial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='avatarmessage',
            options={'managed': True, 'ordering': ['sort']},
        ),
        migrations.AddField(
            model_name='avatarmessage',
            name='sort',
            field=models.PositiveIntegerField(db_index=True, default=0, editable=False),
        ),
    ]
