from unittest import mock

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

    @mock.patch('base.management.commands.import_reddot.Command.load_admission_conditions_for_bachelor')
    @mock.patch('base.management.commands.import_reddot.Command.load_admission_conditions_generic')
    def test_load_admission_conditions(self, mock_generic, mock_bachelor):
        self.command.json_content = [{'year': 2018, 'acronym': 'bacs'}, {'year': 2018, 'acronym': 'actu2m'}]
        self.command.load_admission_conditions()

    def test_set_values_for_text_row_of_condition_admission_raise_exception(self):
        with self.assertRaises(Exception):
            line = {'section': 'demo'}
            self.command.set_values_for_text_row_of_condition_admission(None, line)

    def test_set_values_for_text_row_of_condition_admission(self):
        line = {'section': 'non_university_bachelors', 'text': 'Text'}
        with mock.patch('base.management.commands.import_reddot.Command.set_admission_condition_value'):
            self.command.set_values_for_text_row_of_condition_admission(None, line)

    @mock.patch('base.management.commands.import_reddot.Command.set_admission_condition_value')
    def test_save_text_of_conditions(self, mock_set_admission):
        item = {
            'info': {
                'texts': {
                    'introduction': {'text': 'Introduction'},
                }
            }
        }
        education_group_year = EducationGroupYearFactory()
        admission_condition = AdmissionCondition.objects.create(education_group_year=education_group_year)
        self.command.save_text_of_conditions(admission_condition, item)

        mock_set_admission.assert_called_with(admission_condition, 'free', 'Introduction')

    @mock.patch('base.management.commands.import_reddot.Command.set_admission_condition_value')
    def test_save_text_of_conditions_personalized_access(self, mock_set_admission):
        item = {
            'info': {
                'texts': {
                    'personalized_access': {'text': 'Personalized Access'}
                }
            }
        }
        education_group_year = EducationGroupYearFactory()
        admission_condition = AdmissionCondition.objects.create(education_group_year=education_group_year)
        self.command.save_text_of_conditions(admission_condition, item)

        mock_set_admission.assert_called_with(admission_condition, 'personalized_access', 'Personalized Access')

    @mock.patch('base.management.commands.import_reddot.Command.set_admission_condition_value')
    def test_save_text_of_conditions_not_called(self, mock_set_admission):
        item = {
            'info': {
                'texts': {
                    'test': None,
                }
            }
        }
        education_group_year = EducationGroupYearFactory()
        admission_condition = AdmissionCondition.objects.create(education_group_year=education_group_year)
        self.command.save_text_of_conditions(admission_condition, item)

        mock_set_admission.assert_not_called()

    @mock.patch('base.management.commands.import_reddot.Command.set_admission_condition_value')
    def test_save_text_of_conditions_raise_exception(self, mock_set_admission):
        item = {
            'info': {
                'texts': {
                    'test': 'something',
                }
            }
        }
        education_group_year = EducationGroupYearFactory()
        admission_condition = AdmissionCondition.objects.create(education_group_year=education_group_year)
        with self.assertRaises(Exception):
            self.command.save_text_of_conditions(admission_condition, item)

    @mock.patch('base.management.commands.import_reddot.Command.save_condition_line_of_row')
    @mock.patch('base.management.commands.import_reddot.Command.set_values_for_text_row_of_condition_admission')
    def test_save_diplomas(self, mock_set_values, mock_save_condition):
        item = {'info': {'diplomas': [{'type': 'table'}, {'type': 'text'}]}}
        self.command.save_diplomas(None, item)
        mock_save_condition.assert_called_with(None, {'type': 'table'})
        mock_set_values.assert_called_with(None, {'type': 'text'})
