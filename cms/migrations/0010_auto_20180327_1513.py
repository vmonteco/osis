# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-03-27 13:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0009_auto_20180327_1458'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='textlabel',
            name='deleted',
        ),
        migrations.RemoveField(
            model_name='translatedtext',
            name='deleted',
        ),
        migrations.RemoveField(
            model_name='translatedtextlabel',
            name='deleted',
        ),
    ]
