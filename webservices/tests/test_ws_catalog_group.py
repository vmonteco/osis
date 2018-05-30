##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import json

from django.test import TestCase

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from cms.enums.entity_name import OFFER_YEAR
from cms.tests.factories.text_label import TextLabelFactory
from cms.tests.factories.translated_text import TranslatedTextRandomFactory
from cms.tests.factories.translated_text_label import TranslatedTextLabelFactory
from webservices.tests.helper import Helper


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

    def test_education_group_year_group_with_sections(self):
        education_group_year = EducationGroupYearFactory()

        text_label = TextLabelFactory(entity=OFFER_YEAR,
                                      label='intro')

        translated_text_label = TranslatedTextLabelFactory(
            text_label=text_label,
            language='fr-be',
            label='Introduction'
        )

        translated_text = TranslatedTextRandomFactory(
            language='fr-be',
            text_label=text_label,
            entity=OFFER_YEAR,
            reference=education_group_year.id,
            text='<tag>intro</tag>'
        )

        response = self._get_response(
            education_group_year.academic_year.year,
            'fr',
            education_group_year.partial_acronym
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        response_json = json.loads(response.content.decode('utf-8'))

        self.assertDictEqual(response_json, {
            'acronym': education_group_year.acronym,
            'partial_acronym': education_group_year.partial_acronym,
            'title': education_group_year.title,
            'year': education_group_year.academic_year.year,
            'language': 'fr',
            'sections': [{
                'content': translated_text.text,
                'id': text_label.label,
                'label': translated_text_label.label,
            }]
        })
