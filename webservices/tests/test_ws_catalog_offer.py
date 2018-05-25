import json
import unittest

from django.test import TestCase
from prettyprinter import cpprint

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from cms.enums.entity_name import OFFER_YEAR
from cms.models.translated_text_label import TranslatedTextLabel
from cms.tests.factories.text_label import TextLabelFactory
from cms.tests.factories.translated_text import TranslatedTextFactory, TranslatedTextRandomFactory
from cms.tests.factories.translated_text_label import TranslatedTextLabelFactory
from webservices.tests.helper import Helper


# Create your tests here.
from webservices.views import get_translated_label_from_translated_text, convert_sections_list_of_dict_to_dict


class CatalogOfferWebServiceTestCase(TestCase, Helper):
    URL_NAME = 'v0.1-ws_catalog_offer'
    maxDiff = None

    def test_year_not_found(self):
        response = self._get_response(1990, 'fr', 'actu2m')
        self.assertEqual(response.status_code, 404)

    def test_language_not_found(self):
        response = self._get_response(2017, 'ch', 'actu2m')
        self.assertEqual(response.status_code, 404)

    def test_acronym_not_found(self):
        response = self._get_response(2017, 'fr', 'XYZ')
        self.assertEqual(response.status_code, 404)

    @unittest.skip(reason="Writing the new tests")
    def test_basic_education_group_year(self):
        academic_year = AcademicYearFactory()
        education_group_year = EducationGroupYearFactory(academic_year=academic_year)

        response = self._get_response(academic_year.year, 'fr', education_group_year.acronym)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        response_json = json.loads(response.content.decode('utf-8'))

        self.assertDictEqual(response_json, {
            'acronym': education_group_year.acronym,
            'title': education_group_year.title,
            'year': academic_year.year,
            'language': 'fr',
            'sections': []
        })

    def _test_education_group_year_with_translation(self, language, iso_language):
        values = self._create_records_for_test_education_group_year(iso_language)

        academic_year, education_group_year, text_label, translated_text, translated_text_label = values

        response = self._get_response(academic_year.year, language, education_group_year.acronym)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        response_json = json.loads(response.content.decode('utf-8'))

        context = {
            'academic_year': academic_year,
            'education_group_year': education_group_year,
            'language': language,
            'text_label': text_label,
            'translated_text': translated_text,
            'translated_text_label': translated_text_label
        }

        fake_response = self._mock_response_dictionary(**context)
        self.assertDictEqual(response_json, fake_response)

    def _create_records_for_test_education_group_year(self, iso_language):
        academic_year = AcademicYearFactory()
        education_group_year = EducationGroupYearFactory(academic_year=academic_year)
        text_label = TextLabelFactory(entity=OFFER_YEAR)
        translated_text_label = TranslatedTextLabelFactory(language=iso_language,
                                                           text_label=text_label)
        translated_text = TranslatedTextFactory(
            text_label=text_label,
            entity=text_label.entity,
            reference=education_group_year.id,
            language=iso_language,
            # text is randomized
        )
        return academic_year, education_group_year, text_label, translated_text, translated_text_label

    def _mock_response_dictionary(self, **kwargs):
        return {
            'acronym': kwargs['education_group_year'].acronym,
            'title': kwargs['education_group_year'].title_english,
            'year': kwargs['academic_year'].year,
            'language': kwargs['language'],
            'sections': [
                {
                    'content': kwargs['translated_text'].text,
                    'label': kwargs['translated_text_label'].label,
                    'id': kwargs['text_label'].label
                }
            ]
        }

    def test_education_group_year_with_translation_fr(self):
        self._test_education_group_year_with_translation('fr', 'fr-be')

    def test_education_group_year_with_translation_en(self):
        self._test_education_group_year_with_translation('en', 'en')

    def test_education_group_year_endswith_2m(self):
        iso_language, language = 'fr-be', 'fr'

        education_group_year = EducationGroupYearFactory(acronym='ACTU2M')

        common_education_group_year = EducationGroupYearFactory(
            acronym='common',
            academic_year=education_group_year.academic_year
        )

        common_text_label = TextLabelFactory(entity=OFFER_YEAR, label='finalites_didactiques')
        common_translated_text_label = TranslatedTextLabelFactory(text_label=common_text_label, language=iso_language, label='Finalités Didactiques')

        finalite_didactiques_translated_text = TranslatedTextRandomFactory(
            language=iso_language,
            text_label=common_text_label,
            entity=OFFER_YEAR,
            reference=common_education_group_year.id,
            text='<tag>finalites didactiques</tag>'
        )

        response = self._get_response(education_group_year.academic_year.year, language, education_group_year.acronym)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        response_json = json.loads(response.content.decode('utf-8'))

        self.maxDiff = None

        response_sections = convert_sections_list_of_dict_to_dict(response_json.pop('sections', []))

        self.assertDictEqual(response_json, {
            'acronym': education_group_year.acronym,
            'language': 'fr',
            'title': education_group_year.title,
            'year': education_group_year.academic_year.year,
        })

        sections = [{
            'id': finalite_didactiques_translated_text.text_label.label.replace('_', '-') + '-commun',
            'label': common_translated_text_label.label,
            'content': finalite_didactiques_translated_text.text,
        }]

        sections = convert_sections_list_of_dict_to_dict(sections)

        self.assertDictEqual(response_sections, sections)

    def test_education_group_year_caap(self):
        iso_language, language = 'fr-be', 'fr'

        education_group_year = EducationGroupYearFactory(acronym='ACTU2M')

        common_education_group_year = EducationGroupYearFactory(
            acronym='common',
            academic_year=education_group_year.academic_year
        )

        text_label = TextLabelFactory(entity=OFFER_YEAR, label='caap')
        translated_text_label = TranslatedTextLabelFactory(text_label=text_label,
                                                           language=iso_language,
                                                           label='Caap')

        common_translated_text = TranslatedTextRandomFactory(
            language=iso_language,
            text_label=text_label,
            entity=OFFER_YEAR,
            reference=common_education_group_year.id,
        )

        translated_text = TranslatedTextRandomFactory(
            text_label=text_label,
            entity=text_label.entity,
            reference=education_group_year.id,
            language=iso_language,
        )

        response = self._get_response(education_group_year.academic_year.year, language, education_group_year.acronym)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')

        response_json = json.loads(response.content.decode('utf-8'))

        response_sections = convert_sections_list_of_dict_to_dict(response_json.pop('sections', []))

        self.assertDictEqual(response_json, {
            'acronym': education_group_year.acronym,
            'language': 'fr',
            'title': education_group_year.title,
            'year': education_group_year.academic_year.year,
        })

        sections = [
            {
                'content': translated_text.text,
                'id': translated_text.text_label.label,
                'label': translated_text_label.label,
            },
            {
                'content': common_translated_text.text,
                'id': common_translated_text.text_label.label + '-commun',
                'label': get_translated_label_from_translated_text(common_translated_text),
            }
        ]

        sections = convert_sections_list_of_dict_to_dict(sections)

        self.assertDictEqual(response_sections, sections)


