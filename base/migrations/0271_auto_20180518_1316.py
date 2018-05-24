# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-05-18 11:16
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0270_auto_20180514_1112'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalLearningUnitYear',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('changed', models.DateTimeField(auto_now=True, null=True)),
                ('external_acronym', models.CharField(db_index=True, max_length=15, verbose_name='external_code')),
                ('external_credits', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(500)])),
                ('url', models.URLField(blank=True, max_length=255, null=True)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Entity')),
                ('learning_unit_year', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='base.LearningUnitYear')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='externallearningunityear',
            unique_together=set([('learning_unit_year', 'external_acronym')]),
        ),
    ]