# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-27 15:02
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0180_populate_learning_container_uuid'),
    ]

    operations = [

        migrations.AlterField(
            model_name='learningcontainer',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
    ]