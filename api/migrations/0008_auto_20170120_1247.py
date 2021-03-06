# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-20 12:47
from __future__ import unicode_literals

from django.db import migrations, models
import djchoices.choices


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20170120_1243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='status',
            field=models.CharField(choices=[('scheduled', 'SCHEDULED'), ('active', 'ACTIVE'), ('completed', 'COMPLETED')], default='scheduled', max_length=50, validators=[djchoices.choices.ChoicesValidator({'active': 'ACTIVE', 'completed': 'COMPLETED', 'scheduled': 'SCHEDULED'})]),
        ),
    ]
