# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-20 12:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_match_tournament'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='isActive',
            field=models.BooleanField(default=False),
        ),
    ]
