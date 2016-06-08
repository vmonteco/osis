# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-06-07 15:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0054_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examenrollment',
            name='justification_draft',
            field=models.CharField(blank=True, choices=[('ABSENCE_UNJUSTIFIED', 'ABSENCE_UNJUSTIFIED'), ('ABSENCE_JUSTIFIED', 'ABSENCE_JUSTIFIED'), ('CHEATING', 'CHEATING'), ('SCORE_MISSING', 'SCORE_MISSING')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='examenrollment',
            name='justification_final',
            field=models.CharField(blank=True, choices=[('ABSENCE_UNJUSTIFIED', 'ABSENCE_UNJUSTIFIED'), ('ABSENCE_JUSTIFIED', 'ABSENCE_JUSTIFIED'), ('CHEATING', 'CHEATING'), ('SCORE_MISSING', 'SCORE_MISSING')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='examenrollment',
            name='justification_reencoded',
            field=models.CharField(blank=True, choices=[('ABSENCE_UNJUSTIFIED', 'ABSENCE_UNJUSTIFIED'), ('ABSENCE_JUSTIFIED', 'ABSENCE_JUSTIFIED'), ('CHEATING', 'CHEATING'), ('SCORE_MISSING', 'SCORE_MISSING')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='examenrollmenthistory',
            name='justification_final',
            field=models.CharField(choices=[('ABSENCE_UNJUSTIFIED', 'ABSENCE_UNJUSTIFIED'), ('ABSENCE_JUSTIFIED', 'ABSENCE_JUSTIFIED'), ('CHEATING', 'CHEATING'), ('SCORE_MISSING', 'SCORE_MISSING')], max_length=20, null=True),
        ),
    ]
