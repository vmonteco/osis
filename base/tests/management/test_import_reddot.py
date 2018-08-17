from django.test import TestCase

from base.management.commands import import_reddot
from base.models.admission_condition import AdmissionCondition, AdmissionConditionLine
from base.models.education_group_year import EducationGroupYear
from base.tests.factories.education_group_year import EducationGroupYearFactory


class ImportReddotTestCase(TestCase):
    def setUp(self):
        self.command = import_reddot.Command()
        lang = 'fr-be'
        self.command.suffix_language = '' if lang == 'fr-be' else '_en'

    def test_load_admission_conditions_for_bachelor(self):
        education_group_year_common = EducationGroupYearFactory(acronym='common')
        item = {
            'year': education_group_year_common.academic_year.year,
            'acronym': 'bacs',
            'info': {
                'alert_message': {'text-common': 'Alert Message'},
                'ca_bacs_cond_generales': {'text-common': 'General Conditions'},
                'ca_bacs_cond_particulieres': {'text-common': 'Specific Conditions'},
                'ca_bacs_examen_langue': {'text-common': 'Language Exam'},
                'ca_bacs_cond_speciales': {'text-common': 'Special Conditions'},
            }
        }

        self.command.load_admission_conditions_for_bachelor(item, education_group_year_common.academic_year.year)

        common_bacs = EducationGroupYear.objects.filter(academic_year=education_group_year_common.academic_year,
                                                        acronym='common-bacs').first()

        admission_condition = AdmissionCondition.objects.get(education_group_year=common_bacs)
        self.assertEqual(admission_condition.text_alert_message,
                         item['info']['alert_message']['text-common'])
        self.assertEqual(admission_condition.text_ca_bacs_cond_generales,
                         item['info']['ca_bacs_cond_generales']['text-common'])
        self.assertEqual(admission_condition.text_ca_bacs_cond_particulieres,
                         item['info']['ca_bacs_cond_particulieres']['text-common'])
        self.assertEqual(admission_condition.text_ca_bacs_examen_langue,
                         item['info']['ca_bacs_examen_langue']['text-common'])
        self.assertEqual(admission_condition.text_ca_bacs_cond_speciales,
                         item['info']['ca_bacs_cond_speciales']['text-common'])

    def test_save_condition_line_of_row_with_no_admission_condition_line(self):
        education_group_year = EducationGroupYearFactory()

        admission_condition = AdmissionCondition.objects.create(education_group_year=education_group_year)

        self.assertEqual(AdmissionConditionLine.objects.filter(admission_condition=admission_condition).count(), 0)

        line = {
            'type': 'table',
            'title': 'ucl_bachelors',
            'diploma': 'Diploma',
            'conditions': 'Conditions',
            'access': 'Access',
            'remarks': 'Remarks',
            'external_id': '1234567890'
        }
        self.command.save_condition_line_of_row(admission_condition, line)

        queryset = AdmissionConditionLine.objects.filter(admission_condition=admission_condition)
        self.assertEqual(queryset.count(), 1)

        admission_condition_line = queryset.first()

        self.assertEqual(admission_condition_line.diploma, line['diploma'])
        self.assertEqual(admission_condition_line.conditions, line['conditions'])
        self.assertEqual(admission_condition_line.access, line['access'])
        self.assertEqual(admission_condition_line.remarks, line['remarks'])

    def test_save_condition_line_of_row_with_admission_condition_line(self):
        education_group_year = EducationGroupYearFactory()

        line = {
            'type': 'table',
            'title': 'ucl_bachelors',
            'diploma': 'Diploma',
            'conditions': 'Conditions',
            'access': 'Access',
            'remarks': 'Remarks',
            'external_id': '1234567890'
        }

        admission_condition = AdmissionCondition.objects.create(education_group_year=education_group_year)

        queryset = AdmissionConditionLine.objects.filter(admission_condition=admission_condition)
        self.assertEqual(queryset.count(), 0)

        acl = AdmissionConditionLine.objects.create(admission_condition=admission_condition,
                                                    section=line['title'],
                                                    external_id=line['external_id'])
        self.assertEqual(queryset.count(), 1)

        self.command.save_condition_line_of_row(admission_condition, line)

        queryset = AdmissionConditionLine.objects.filter(admission_condition=admission_condition)
        self.assertEqual(queryset.count(), 1)

        admission_condition_line = queryset.first()

        self.assertEqual(admission_condition_line.diploma, line['diploma'])
        self.assertEqual(admission_condition_line.conditions, line['conditions'])
        self.assertEqual(admission_condition_line.access, line['access'])
        self.assertEqual(admission_condition_line.remarks, line['remarks'])
