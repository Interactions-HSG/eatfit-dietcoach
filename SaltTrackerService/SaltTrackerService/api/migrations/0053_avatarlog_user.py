# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-06-20 15:06
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0052_auto_20170620_1504'),
    ]

    operations = [
        migrations.AddField(
            model_name='avatarlog',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
