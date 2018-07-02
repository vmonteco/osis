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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import uuid
from copy import copy
from unittest.mock import patch

from django.test import TestCase

from base.models.enums.learning_unit_year_subtypes import FULL
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.business.learning_units import GenerateAcademicYear
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from cms.tests.factories.translated_text import TranslatedTextFactory
from reference.tests.factories.language import LanguageFactory
from base.forms.learning_unit_pedagogy import LearningUnitPedagogyEditForm
from cms.enums import entity_name


class TestValidation(TestCase):
    def setUp(self):
        self.language = LanguageFactory(code="EN")
        self.current_ac = create_current_academic_year()
        self._build_multiple_learningunityears()
        self.cms_translated_text = TranslatedTextFactory(
            entity=entity_name.LEARNING_UNIT_YEAR,
            reference=self.luys[self.current_ac.year].id,
            language='EN',
            text='Text random'
        )
        self.valid_form_data = _get_valid_form_data(self.cms_translated_text)

    def test_invalid_form(self):
        del self.valid_form_data['cms_id']
        form = LearningUnitPedagogyEditForm(self.valid_form_data)
        self.assertFalse(form.is_valid())

    def test_valid_form(self):
        form = LearningUnitPedagogyEditForm(self.valid_form_data)
        self.assertEqual(form.errors, {})
        self.assertTrue(form.is_valid())

    @patch("cms.models.translated_text.update_or_create")
    def test_save_without_postponement(self, mock_update_or_create):
        """In this test, we ensure that if we modify UE of N or N-... => The postponement is not done"""
        form = LearningUnitPedagogyEditForm(self.valid_form_data)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        mock_update_or_create.assert_called_once_with(entity=self.cms_translated_text.entity,
                                                      reference=self.cms_translated_text.reference,
                                                      language=self.cms_translated_text.language,
                                                      text_label=self.cms_translated_text.text_label,
                                                      text=self.cms_translated_text.text)

    @patch("cms.models.translated_text.update_or_create")
    def test_save_with_postponement(self, mock_update_or_create):
        """In this test, we ensure that if we modify UE of N+1 or N+X => The postponement until the lastest UE"""
        luy_in_future = self.luys[self.current_ac.year + 1]
        cms_pedagogy_future = TranslatedTextFactory(
            entity=entity_name.LEARNING_UNIT_YEAR,
            reference=luy_in_future.id,
            language='EN',
            text='Text in future'
        )
        form = LearningUnitPedagogyEditForm(data=_get_valid_form_data(cms_pedagogy_future))
        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        # N+1 ===> N+6
        self.assertEqual(mock_update_or_create.call_count, 5)

    def _build_multiple_learningunityears(self):
        self.luys = {
            self.current_ac.year:  LearningUnitYearFactory(
                learning_container_year__academic_year=self.current_ac,
                academic_year=self.current_ac,
                acronym="LBIR1200",
                subtype=FULL
            )
        }
        # Create multiple academic year
        self.ac_years_containers = GenerateAcademicYear(start_year=self.current_ac.year + 1,
                                                        end_year=self.current_ac.year + 5)
        # Duplicate learning unit year full with different academic year
        for ac_year in self.ac_years_containers.academic_years:
            new_luy = copy(self.luys[self.current_ac.year])
            new_luy.pk = None
            new_luy.uuid = uuid.uuid4()
            new_luy.academic_year = ac_year
            new_luy.save()
            self.luys[ac_year.year] = new_luy


def _get_valid_form_data(cms_translated_text):
    return {
        "trans_text": getattr(cms_translated_text, 'text'),
        "cms_id": getattr(cms_translated_text, 'id'),
        "reference": getattr(cms_translated_text, 'reference')
    }
