# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-20 12:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_tournament_isactive'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slack_name', models.CharField(max_length=120)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.AlterField(
            model_name='match',
            name='away',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='away', to='api.Profile'),
        ),
        migrations.AlterField(
            model_name='match',
            name='home',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='home', to='api.Profile'),
        ),
        migrations.AddField(
            model_name='profile',
            name='team',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='api.Team'),
        ),
    ]
