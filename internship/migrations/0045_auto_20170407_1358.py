# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-04-07 11:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0044_auto_20170406_1053'),
    ]

    operations = [
        migrations.RunSQL("select setval('internship_internship_id_seq', 10);")
    ]