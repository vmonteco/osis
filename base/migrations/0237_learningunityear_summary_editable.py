# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-03-02 08:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0236_auto_20180312_1035'),
    ]

    operations = [
        migrations.AddField(
            model_name='learningunityear',
            name='summary_editable',
            field=models.BooleanField(default=True),
        ),
    ]