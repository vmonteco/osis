import json

from django.test import TestCase

# Create your tests here.
from django.urls import reverse

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from cms.enums.entity_name import OFFER_YEAR
from cms.tests.factories.text_label import TextLabelFactory
from cms.tests.factories.translated_text import TranslatedTextFactory
from cms.tests.factories.translated_text_label import TranslatedTextLabelFactory


class ReddotWebServiceTestCase(TestCase):
    def _get_url(self, year, language, acronym):
        return reverse('v0.1-ws_catalog_offer',
                       kwargs=dict(year=year, language=language, acronym=acronym))

    def _get_response(self, year, language, acronym):
        return self.client.get(self._get_url(year, language, acronym), format='json')

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

        response = self._get_response(academic_year.year, language, education_group_year.acronym)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        response_json = json.loads(response.content.decode('utf-8'))

        fake_response = self._mock_response_dictionary(academic_year, education_group_year, language, text_label,
                                                       translated_text, translated_text_label)
        self.assertDictEqual(response_json, fake_response)

    def _mock_response_dictionary(self, academic_year, education_group_year, language, text_label, translated_text,
                                  translated_text_label):
        return {
            'acronym': education_group_year.acronym,
            'title': education_group_year.title_english,
            'year': academic_year.year,
            'language': language,
            'sections': [
                {
                    'content': translated_text.text,
                    'label': translated_text_label.label,
                    'id': text_label.label
                }
            ]
        }

    def test_education_group_year_with_translation_fr(self):
        self._test_education_group_year_with_translation('fr', 'fr-be')

    def test_education_group_year_with_translation_en(self):
        self._test_education_group_year_with_translation('en', 'en')
