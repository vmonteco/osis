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
import unittest

from django.test import TestCase

from base.tests.factories.education_group_year import EducationGroupYearFactory
from cms.enums.entity_name import OFFER_YEAR
from cms.models.text_label import TextLabel
from cms.models.translated_text import TranslatedText
from cms.models.translated_text_label import TranslatedTextLabel
from cms.tests.factories.text_label import TextLabelFactory
from cms.tests.factories.translated_text import TranslatedTextRandomFactory
from cms.tests.factories.translated_text_label import TranslatedTextLabelFactory
from webservices.tests.helper import Helper
from webservices.utils import convert_sections_list_of_dict_to_dict


@unittest.skip('Disable this test because we stop to use it')
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

    def _test_education_group_year_with_translation(self, language, iso_language):
        context = self._create_records_for_test_education_group_year(iso_language)

        response = self._get_response(
            context['academic_year'].year,
            language,
            context['education_group_year'].acronym
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        response_json = response.json()

        context['language'] = language

        fake_response = self._mock_response_dictionary(**context)

        self.assertDictEqual(response_json, fake_response)

    def _create_records_for_test_education_group_year(self, iso_language):
        education_group_year = EducationGroupYearFactory()
        text_label = TextLabelFactory(entity=OFFER_YEAR)
        translated_text_label = TranslatedTextLabelFactory(language=iso_language,
                                                           text_label=text_label)
        translated_text = TranslatedTextRandomFactory(
            text_label=text_label,
            entity=text_label.entity,
            reference=education_group_year.id,
            language=iso_language,
        )
        return {
            'academic_year': education_group_year.academic_year,
            'education_group_year': education_group_year,
            'text_label': text_label,
            'translated_text': translated_text,
            'translated_text_label': translated_text_label,
        }

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


class CommonHelper:
    ACRONYM = None
    TERMS = []

    def setUp(self):
        super().setUp()

        self.iso_language, self.language = 'fr-be', 'fr'

        if self.ACRONYM:
            self.education_group_year = EducationGroupYearFactory(acronym=self.ACRONYM)
        else:
            self.education_group_year = EducationGroupYearFactory()

        self.common_education_group_year = EducationGroupYearFactory(
            acronym='common',
            academic_year=self.education_group_year.academic_year
        )

        self.setup_common_terms()

    def setup_common_terms(self):
        for term, label in self.TERMS:
            text_label = TextLabelFactory(entity=OFFER_YEAR, label=term)
            TranslatedTextLabelFactory(
                text_label=text_label,
                language=self.iso_language,
                label=label
            )

            TranslatedTextRandomFactory(
                language=self.iso_language,
                text_label=text_label,
                entity=OFFER_YEAR,
                reference=self.common_education_group_year.id,
                text='<tag>{term}</tag>'.format(term=term)
            )

    def get_common_text_label(self, term):
        return TextLabel.objects.get(entity=OFFER_YEAR, label=term)

    def get_common_translated_text(self, term):
        return TranslatedText.objects.get(
            language=self.iso_language,
            text_label__label=term,
            entity=OFFER_YEAR,
            reference=self.common_education_group_year.id
        )

    def get_common_translated_text_label(self, term):
        return TranslatedTextLabel.objects.get(
            text_label__label=term,
            language=self.iso_language,
        )

    def get_section_for_common_term(self, term):
        key_id = term
        if term != 'agregations':
            key_id = self.get_common_text_label(term).label + '-commun'

        return {
            'label': self.get_common_translated_text_label(term).label,
            'content': self.get_common_translated_text(term).text,
            'id': key_id,
        }

    def create_text_label_and_translation(self, term, label):
        text_label = TextLabelFactory(entity=OFFER_YEAR, label=term)
        translated_text_label = TranslatedTextLabelFactory(
            text_label=text_label,
            language=self.iso_language,
            label=label
        )

        translated_text = TranslatedTextRandomFactory(
            text_label=text_label,
            entity=text_label.entity,
            reference=self.education_group_year.id,
            language=self.iso_language
        )

        return translated_text_label, translated_text

    def get_section_for_term(self, translated_text_label, translated_text):
        return {
            'content': translated_text.text,
            'id': translated_text.text_label.label,
            'label': translated_text_label.label,
        }


@unittest.skip('Disable this test because we stop to use it')
class WsCatalogOfferCommonTestCase(CommonHelper, TestCase, Helper):
    maxDiff = None
    URL_NAME = 'v0.1-ws_catalog_offer'

    TERMS = [
        ('caap', 'Caap'),
        ('prerequis', 'Prérequis'),
        ('module_complementaire', 'Module Complémentaire'),
        ('agregations', 'Agregations')
    ]

    def test_header_of_message(self):
        response = self._get_response(self.education_group_year.academic_year.year,
                                      self.language,
                                      self.education_group_year.acronym)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')

        response_json = response.json()

        self.assertDictEqual(response_json, {
            'acronym': self.education_group_year.acronym,
            'language': self.language,
            'title': self.education_group_year.title,
            'year': self.education_group_year.academic_year.year,
            'sections': [],
        })

    def test_education_group_year_caap(self):
        text_label = self.get_common_text_label('caap')
        translated_text_label = self.get_common_translated_text_label('caap')

        translated_text = TranslatedTextRandomFactory(
            text_label=text_label,
            entity=text_label.entity,
            reference=self.education_group_year.id,
            language=self.iso_language,
        )

        response = self._get_response(
            self.education_group_year.academic_year.year,
            self.language,
            self.education_group_year.acronym
        )

        response_json = response.json()

        response_sections = convert_sections_list_of_dict_to_dict(
            response_json.pop('sections', [])
        )

        sections = [
            self.get_section_for_term(translated_text_label, translated_text),
            self.get_section_for_common_term('caap'),
        ]

        sections = convert_sections_list_of_dict_to_dict(sections)

        self.assertDictEqual(response_sections, sections)

    def test_education_group_year_prerequis(self):
        text_label = self.get_common_text_label('prerequis')
        translated_text_label = self.get_common_translated_text_label('prerequis')

        translated_text = TranslatedTextRandomFactory(
            text_label=text_label,
            entity=text_label.entity,
            reference=self.education_group_year.id,
            language=self.iso_language
        )

        response = self._get_response(
            self.education_group_year.academic_year.year,
            self.language,
            self.education_group_year.acronym
        )

        response_json = response.json()

        response_sections = convert_sections_list_of_dict_to_dict(
            response_json.pop('sections', [])
        )

        sections = [
            self.get_section_for_term(translated_text_label, translated_text),
            self.get_section_for_common_term('prerequis'),
        ]

        sections = convert_sections_list_of_dict_to_dict(sections)

        self.assertDictEqual(response_sections, sections)

    def test_education_group_year_module_complementaire(self):
        text_label = self.get_common_text_label('module_complementaire')
        translated_text_label = self.get_common_translated_text_label('module_complementaire')

        translated_text = TranslatedTextRandomFactory(
            text_label=text_label,
            language=self.iso_language,
            entity=OFFER_YEAR,
            reference=self.education_group_year.id,
        )

        response = self._get_response(
            self.education_group_year.academic_year.year,
            self.language,
            self.education_group_year.acronym,
        )

        response_json = response.json()

        response_sections = convert_sections_list_of_dict_to_dict(
            response_json.pop('sections', [])
        )

        sections = [
            self.get_section_for_term(translated_text_label, translated_text),
            self.get_section_for_common_term('module_complementaire'),
        ]

        sections = convert_sections_list_of_dict_to_dict(sections)

        self.assertDictEqual(response_sections, sections)

    @unittest.skip(reason='In refactoring')
    def test_education_group_year_programme(self):
        translated_text_label, translated_text = \
            self.create_text_label_and_translation('programme', 'Programme')

        response = self._get_response(
            self.education_group_year.academic_year.year,
            self.language,
            self.education_group_year.acronym
        )

        response_json = response.json()

        response_sections = convert_sections_list_of_dict_to_dict(
            response_json.pop('sections', [])
        )

        sections = [
            self.get_section_for_term(translated_text_label, translated_text),
            self.get_section_for_common_term('agregations'),
        ]

        sections = convert_sections_list_of_dict_to_dict(sections)

        self.assertDictEqual(response_sections, sections)


@unittest.skip('Disable this test because we stop to use it')
class WsCatalogOfferCommonTestCaseFor2M(CommonHelper, TestCase, Helper):
    URL_NAME = 'v0.1-ws_catalog_offer'
    ACRONYM = 'ACTU2M'

    TERMS = [
        ('finalites_didactiques', 'Finalités Didactiques'),
        ('caap', 'Caap'),
    ]

    def test_header_of_message(self):
        response = self._get_response(self.education_group_year.academic_year.year,
                                      self.language,
                                      self.education_group_year.acronym)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')

        response_json = response.json()

        self.assertDictEqual(response_json, {
            'acronym': self.education_group_year.acronym,
            'language': self.language,
            'title': self.education_group_year.title,
            'year': self.education_group_year.academic_year.year,
            'sections': [
                self.get_section_for_common_term('finalites_didactiques')
            ],
        })

    def test_education_group_year_endswith_2m(self):
        response = self._get_response(self.education_group_year.academic_year.year,
                                      self.language,
                                      self.education_group_year.acronym)

        response_json = response.json()

        response_sections = convert_sections_list_of_dict_to_dict(
            response_json.pop('sections', [])
        )

        sections = [
            self.get_section_for_common_term('finalites_didactiques')
        ]

        sections = convert_sections_list_of_dict_to_dict(sections)

        self.assertDictEqual(response_sections, sections)

    def test_education_group_year_caap(self):
        text_label = self.get_common_text_label('caap')
        translated_text_label = self.get_common_translated_text_label('caap')

        translated_text = TranslatedTextRandomFactory(
            text_label=text_label,
            entity=text_label.entity,
            reference=self.education_group_year.id,
            language=self.iso_language,
        )

        response = self._get_response(
            self.education_group_year.academic_year.year,
            self.language,
            self.education_group_year.acronym
        )

        response_json = response.json()

        response_sections = convert_sections_list_of_dict_to_dict(
            response_json.pop('sections', [])
        )

        sections = [
            self.get_section_for_term(translated_text_label, translated_text),
            self.get_section_for_common_term('caap'),
            self.get_section_for_common_term('finalites_didactiques')
        ]

        sections = convert_sections_list_of_dict_to_dict(sections)

        self.assertDictEqual(response_sections, sections)


class WsCatalogOfferPostTestCase(TestCase, Helper):
    URL_NAME = 'v0.1-ws_catalog_offer'

    def test_year_not_found(self):
        response = self.post(1990, 'fr', 'actu2m', data={})
        self.assertEqual(response.status_code, 404)

    def test_string_year_not_found(self):
        response = self.post('1990', 'fr', 'actu2m', data={})
        self.assertEqual(response.status_code, 404)

    def test_language_not_found(self):
        response = self.post(2017, 'ch', 'actu2m', data={})
        self.assertEqual(response.status_code, 404)

    def test_acronym_not_found(self):
        response = self.post(2017, 'fr', 'XYZ', data={})
        self.assertEqual(response.status_code, 404)

    def test_01(self):
        education_group_year = EducationGroupYearFactory(acronym='ACTU2M')

        common_education_group_year = EducationGroupYearFactory(
            acronym='common',
            academic_year=education_group_year.academic_year
        )

        iso_language, language = 'fr-be', 'fr'

        message = {
            "sections": [
                "welcome_job",
                "welcome_profil",
                "welcome_programme",
                "welcome_introduction",
                "cond_admission",
                "infos_pratiques",
                "caap",
                "caap-commun",
                "contacts",
                "structure",
                "acces_professions",
                "comp_acquis",
                "pedagogie",
                "formations_accessibles",
                "evaluation",
                "mobilite",
                "programme_detaille",
                "certificats",
                "module_complementaire",
                "module_complementaire-commun",
                "prerequis",
                "prerequis-commun",
                "intro-lactu200t",
                "intro-lactu200s",
                "options",
                "intro-lactu200o",
                "intro-lsst100o"
            ]
        }

        ega = EducationGroupYearFactory(partial_acronym='lactu200t',
                                        academic_year=education_group_year.academic_year)
        text_label = TextLabelFactory(entity='offer_year', label='intro')
        TranslatedTextLabelFactory(text_label=text_label,
                                   language=iso_language)
        TranslatedTextRandomFactory(text_label=text_label,
                                    language=iso_language,
                                    reference=ega.id,
                                    entity=text_label.entity)

        text_label = TextLabelFactory(entity='offer_year', label='prerequis')
        TranslatedTextLabelFactory(text_label=text_label,
                                   language=iso_language)
        TranslatedTextRandomFactory(text_label=text_label,
                                    language=iso_language,
                                    reference=education_group_year.id,
                                    entity=text_label.entity)

        TranslatedTextRandomFactory(text_label=text_label,
                                    language=iso_language,
                                    reference=common_education_group_year.id,
                                    entity=text_label.entity)

        text_label = TextLabelFactory(entity='offer_year', label='caap')
        TranslatedTextLabelFactory(text_label=text_label,
                                   language=iso_language)
        TranslatedTextRandomFactory(text_label=text_label,
                                    language=iso_language,
                                    reference=education_group_year.id,
                                    entity=text_label.entity)

        TranslatedTextRandomFactory(text_label=text_label,
                                    language=iso_language,
                                    reference=common_education_group_year.id,
                                    entity=text_label.entity)

        response = self.post(
            education_group_year.academic_year.year,
            language,
            education_group_year.acronym,
            data=message,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')

    def test_without_any_sections(self):
        education_group_year = EducationGroupYearFactory()

        common_education_group_year = EducationGroupYearFactory(
            acronym='common',
            academic_year=education_group_year.academic_year,
        )

        text_label = TextLabelFactory(entity='offer_year')

        for iso_language, language in [('fr-be', 'fr'), ('en', 'en')]:
            with self.subTest(iso_language=iso_language, language=language):
                TranslatedTextLabelFactory(text_label=text_label,
                                           language=iso_language)
                TranslatedTextRandomFactory(text_label=text_label,
                                            language=iso_language,
                                            reference=common_education_group_year.id,
                                            entity=text_label.entity)
                message = {
                    'sections': [
                        'welcome_job',
                    ]
                }

                response = self.post(
                    education_group_year.academic_year.year,
                    language,
                    education_group_year.acronym,
                    data=message
                )

                response_json = response.json()

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content_type, 'application/json')

                title_to_test = education_group_year.title if language == 'fr' else education_group_year.title_english
                self.assertDictEqual(response_json, {
                    'acronym': education_group_year.acronym,
                    'language': language,
                    'sections': [],
                    'title': title_to_test,
                    'year': education_group_year.academic_year.year,
                })

    def test_with_one_section(self):
        education_group_year = EducationGroupYearFactory()

        text_label = TextLabelFactory(entity='offer_year', label='caap')

        for iso_language, language in [('fr-be', 'fr'), ('en', 'en')]:
            with self.subTest(iso_language=iso_language, language=language):
                ttl = TranslatedTextLabelFactory(text_label=text_label,
                                                 language=iso_language)
                tt = TranslatedTextRandomFactory(text_label=text_label,
                                                 language=iso_language,
                                                 reference=education_group_year.id,
                                                 entity=text_label.entity)

                message = {
                    'sections': [
                        text_label.label,
                    ]
                }

                response = self.post(
                    education_group_year.academic_year.year,
                    language,
                    education_group_year.acronym,
                    data=message
                )

                response_json = response.json()

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content_type, 'application/json')

                title_to_test = education_group_year.title if language == 'fr' else education_group_year.title_english

                self.assertDictEqual(response_json, {
                    'acronym': education_group_year.acronym,
                    'language': language,
                    'title': title_to_test,
                    'year': education_group_year.academic_year.year,
                    'sections': [{
                        'label': ttl.label,
                        'id': tt.text_label.label,
                        'content': tt.text,
                    }]
                })

    def test_with_one_section_with_common(self):
        education_group_year = EducationGroupYearFactory()

        common_education_group_year = EducationGroupYearFactory(
            acronym='common',
            academic_year=education_group_year.academic_year,
        )

        text_label = TextLabelFactory(entity='offer_year', label='caap')

        for iso_language, language in [('fr-be', 'fr'), ('en', 'en')]:
            with self.subTest(iso_language=iso_language, language=language):
                ttl = TranslatedTextLabelFactory(text_label=text_label,
                                                 language=iso_language)
                tt = TranslatedTextRandomFactory(text_label=text_label,
                                                 language=iso_language,
                                                 reference=education_group_year.id,
                                                 entity=text_label.entity)

                tt2 = TranslatedTextRandomFactory(text_label=text_label,
                                                  language=iso_language,
                                                  reference=common_education_group_year.id,
                                                  entity=text_label.entity)

                message = {
                    'sections': [
                        text_label.label,
                        text_label.label + '-commun'
                    ]
                }

                response = self.post(
                    education_group_year.academic_year.year,
                    language,
                    education_group_year.acronym,
                    data=message
                )

                response_json = response.json()

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content_type, 'application/json')

                title_to_test = education_group_year.title if language == 'fr' else education_group_year.title_english

                response_sections = convert_sections_list_of_dict_to_dict(
                    response_json.pop('sections', [])
                )

                self.assertDictEqual(response_json, {
                    'acronym': education_group_year.acronym,
                    'language': language,
                    'title': title_to_test,
                    'year': education_group_year.academic_year.year,
                })

                sections = [{
                    'id': tt.text_label.label,
                    'label': ttl.label,
                    'content': tt.text,
                }, {
                    'id': tt.text_label.label + '-commun',
                    'label': ttl.label,
                    'content': tt2.text,
                }]
                sections = convert_sections_list_of_dict_to_dict(sections)

                self.assertDictEqual(response_sections, sections)

    def test_02(self):
        education_group_year = EducationGroupYearFactory(acronym='ACTU2M')

        common_education_group_year = EducationGroupYearFactory(
            acronym='common',
            academic_year=education_group_year.academic_year
        )

        iso_language, language = 'fr-be', 'fr'

        sections = [
            "welcome_job",
            "welcome_profil",
            "welcome_programme",
            "welcome_introduction",
            "cond_admission",
            "infos_pratiques",
            "caap",
            "caap-commun",
            "contacts",
            "structure",
            "acces_professions",
            "comp_acquis",
            "pedagogie",
            "formations_accessibles",
            "evaluation",
            "mobilite",
            "programme_detaille",
            "certificats",
            "module_complementaire",
            "module_complementaire-commun",
            "prerequis",
            "prerequis-commun",
            "intro-lactu200t",
            "intro-lactu200s",
            "options",
            "intro-lactu200o",
            "intro-lsst100o"
        ]

        sections_set, common_sections_set, intro_set = set(), set(), set()

        for section in sections:
            if section.startswith('intro-'):
                intro_set.add(section[len('intro-'):])
                continue
            if section.endswith('-commun'):
                section = section[:-len('-commun')]
                common_sections_set.add(section)
            sections_set.add(section)

        for section in sections_set:
            text_label = TextLabelFactory(entity='offer_year', label=section)
            TranslatedTextLabelFactory(text_label=text_label, language=iso_language)

            TranslatedTextRandomFactory(text_label=text_label,
                                        language=iso_language,
                                        reference=education_group_year.id,
                                        entity=text_label.entity,
                                        text='<tag>{section}</tag>'.format(section=section))

            if section in common_sections_set:
                TranslatedTextRandomFactory(text_label=text_label,
                                            language=iso_language,
                                            reference=common_education_group_year.id,
                                            entity=text_label.entity,
                                            text='<tag>{section}-commun</tag>'.format(section=section))

        text_label = TextLabelFactory(entity='offer_year', label='intro')
        TranslatedTextLabelFactory(text_label=text_label,
                                   language=iso_language)

        for section in intro_set:
            ega = EducationGroupYearFactory(partial_acronym=section, academic_year=education_group_year.academic_year)
            TranslatedTextRandomFactory(text_label=text_label,
                                        language=iso_language,
                                        reference=ega.id,
                                        entity=text_label.entity,
                                        text='<tag>intro-{section}</tag>'.format(section=section))

        message = {
            "sections": sections,
        }

        response = self.post(
            education_group_year.academic_year.year,
            language,
            education_group_year.acronym,
            data=message,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')

        response_json = response.json()

        response_sections = convert_sections_list_of_dict_to_dict(response_json.pop('sections', []))

        for section in sections_set:
            if section in response_sections:
                response_sections.pop(section)

        self.assertEqual(len(response_sections), len(intro_set) + len(common_sections_set))
        for section in common_sections_set:
            if section + '-commun' in response_sections:
                response_sections.pop(section + '-commun')

        self.assertEqual(len(response_sections), len(intro_set))
        for section in intro_set:
            if 'intro-' + section in response_sections:
                response_sections.pop('intro-' + section)

        self.assertEqual(len(response_sections), 0)

    def test_no_translation_for_term(self):
        education_group_year = EducationGroupYearFactory()

        iso_language, language = 'fr-be', 'fr'

        text_label = TextLabelFactory(entity='offer_year')
        translated_text_label = TranslatedTextLabelFactory(text_label=text_label, language=iso_language)

        message = {
            'sections': [text_label.label]
        }

        response = self.post(
            year=education_group_year.academic_year.year,
            language=language,
            acronym=education_group_year.acronym,
            data=message
        )
        response_json = response.json()
        response_sections = convert_sections_list_of_dict_to_dict(response_json.pop('sections', []))

        sections = convert_sections_list_of_dict_to_dict([{
            'id': text_label.label,
            'label': translated_text_label.label,
            'content': None
        }])

        self.assertEqual(response_sections, sections)

    def test_no_corresponding_term(self):
        education_group_year = EducationGroupYearFactory()

        iso_language, language = 'fr-be', 'fr'

        message = {
            'sections': ['demo']
        }

        response = self.post(
            year=education_group_year.academic_year.year,
            language=language,
            acronym=education_group_year.acronym,
            data=message
        )
        response_json = response.json()
        response_sections = convert_sections_list_of_dict_to_dict(response_json.pop('sections', []))

        self.assertEqual(len(response_sections), 0)
