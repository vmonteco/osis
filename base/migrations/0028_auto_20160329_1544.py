# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-29 13:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0027_auto_20160329_1527'),
    ]

    operations = [
        migrations.AlterField(
            model_name='option',
            name='order',
            field=models.IntegerField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='order',
            field=models.IntegerField(blank=True, max_length=10, null=True),
        ),
    ]
