import json
import textwrap
import unittest

from django.http import Http404
from django.test import TestCase
# Create your tests here.
from django.urls import reverse

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from cms.enums.entity_name import OFFER_YEAR
from cms.tests.factories.text_label import TextLabelFactory
from cms.tests.factories.translated_text import TranslatedTextFactory
from cms.tests.factories.translated_text_label import TranslatedTextLabelFactory
from webservices.views import get_title_of_education_group_year, to_int_or_404, normalize_module_complementaire, \
    normalize_program, normalize_caap_or_prerequis


class Helper:
    def _get_url(self, year, language, acronym):
        return reverse(self.URL_NAME,
                       kwargs=dict(year=year, language=language, acronym=acronym))

    def _get_response(self, year, language, acronym):
        return self.client.get(self._get_url(year, language, acronym), format='json')



class CatalogOfferWebServiceTestCase(TestCase, Helper):
    URL_NAME = 'v0.1-ws_catalog_offer'

    def test_year_not_found(self):
        response = self._get_response(1990, 'fr', 'actu2m')
        self.assertEqual(response.status_code, 404)

    def test_language_not_found(self):
        response = self._get_response(2017, 'ch', 'actu2m')
        self.assertEqual(response.status_code, 404)

    def test_acronym_not_found(self):
        response = self._get_response(2017, 'fr', 'XYZ')
        self.assertEqual(response.status_code, 404)

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


class CatalogGroupWebServiceTestCase(TestCase, Helper):
    URL_NAME = 'v0.1-ws_catalog_group'

    def test_year_not_found(self):
        response = self._get_response(1990, 'fr', 'actu2m')
        self.assertEqual(response.status_code, 404)

    def test_language_not_found(self):
        response = self._get_response(2017, 'ch', 'actu2m')
        self.assertEqual(response.status_code, 404)

    def test_acronym_not_found(self):
        response = self._get_response(2017, 'fr', 'XYZ')
        self.assertEqual(response.status_code, 404)


    def test_basic_education_group_year_group(self):
        academic_year = AcademicYearFactory()
        education_group_year = EducationGroupYearFactory(academic_year=academic_year)

        response = self._get_response(academic_year.year, 'fr',
                                      education_group_year.partial_acronym)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        response_json = json.loads(response.content.decode('utf-8'))

        self.assertDictEqual(response_json, {
            'acronym': education_group_year.acronym,
            'partial_acronym': education_group_year.partial_acronym,
            'title': education_group_year.title,
            'year': academic_year.year,
            'language': 'fr',
            'sections': []
        })


class UtilsTestCase(unittest.TestCase):
    def test_with_404(self):
        with self.assertRaises(Http404):
            to_int_or_404('salut')

    def test_no_404(self):
        result = to_int_or_404('10')
        self.assertEqual(result, 10)


class GetTitleOrEducationGroupYear_TestCase(TestCase):
    def test_get_title_or_education_group_year(self):
        ega = EducationGroupYearFactory(title='french', title_english='english')

        title = get_title_of_education_group_year(ega, 'fr-be')
        self.assertEqual('french', title)

        title = get_title_of_education_group_year(ega, 'en')
        self.assertEqual('english', title)


class NormalizationTestCase(TestCase):
    def test_normalize_module_complementaire(self):
        common_terms = {'module_compl': 'Information'}
        has_section = {}
        content = normalize_module_complementaire(
            common_terms,
            'Message',
            has_section,
            'section'
        )
        self.assertEqual(
            content,
            textwrap.dedent('<div class="info">Information</div>Message')
        )

        self.assertIn('section', has_section)

    def test_normalize_module_complementaire_no_term(self):
        content = normalize_module_complementaire(
            {}, 'Message',
            {}, 'section'
        )

        self.assertEqual(
            content,
            textwrap.dedent('Message')
        )


    def test_normalize_program(self):
        common_terms = {'agregations': 'Agregation'}
        has_section = {}
        content = normalize_program(
            common_terms,
            'Message',
            has_section,
            'section'
        )
        self.assertEqual(
            content,
            textwrap.dedent('AgregationMessage')
        )

        self.assertIn('section', has_section)

    def test_normalize_program_no_term(self):
        content = normalize_program(
            {}, 'Message',
            {}, 'section'
        )

        self.assertEqual(
            content,
            textwrap.dedent('Message')
        )


    def test_normalize_caap_or_prerequis(self):
        common_terms = {'section': 'Caap'}
        has_section = {}
        content = normalize_caap_or_prerequis(
            common_terms,
            'Message<div class="part2">Hello</div>',
            has_section,
            'section'
        )
        self.assertEqual(
            content,
            textwrap.dedent('MessageCaap<div class="part2">Hello</div>')
        )

        self.assertIn('section', has_section)

    def test_normalize_caap_or_prerequis_no_term(self):
        common_terms = {'section': 'Caap'}
        has_section = {}
        content = normalize_caap_or_prerequis(
            common_terms,
            'Message<div class="part2">Hello</div>',
            has_section,
            ''
        )
        self.assertEqual(
            content,
            textwrap.dedent('Message<div class="part2">Hello</div>')
        )
