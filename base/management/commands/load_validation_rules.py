#!/usr/bin/env python
import csv

from django.core.management.base import BaseCommand

from base.models.validation_rule import ValidationRule


class Command(BaseCommand):
    def handle(self, *args, **options):
        path = "base/fixtures/validation_rules.csv"
        self.load_csv(path)

    @staticmethod
    def load_csv(path):
        with open(path) as f:
            reader = csv.reader(f)
            titles = next(reader)

            for row in reader:
                _, created = ValidationRule.objects.get_or_create(
                    field_reference=row[1],
                    status_field=row[2],
                    initial_value=row[3],
                    regex_rule=row[4],
                    regex_error_message=row[5],
                )
