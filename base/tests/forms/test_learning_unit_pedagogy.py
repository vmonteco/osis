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

from django.conf import settings
from django.contrib.auth.models import Permission
from django.test import TestCase

from base.forms.learning_unit_pedagogy import LearningUnitPedagogyEditForm, teachingmaterialformset_factory, \
    SummaryModelForm
from base.models.enums.learning_unit_year_subtypes import FULL
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.business.learning_units import GenerateAcademicYear
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.teaching_material import TeachingMaterialFactory
from cms.enums import entity_name
from cms.tests.factories.text_label import TextLabelFactory
from cms.tests.factories.translated_text import TranslatedTextFactory
from reference.tests.factories.language import LanguageFactory


class LearningUnitPedagogyContextMixin(TestCase):
    """"This mixin is used in this test file in order to setup an environment for testing pedagogy"""
    def setUp(self):
        self.language = LanguageFactory(code="EN")
        self.person = PersonFactory()
        self.person.user.user_permissions.add(Permission.objects.get(codename="can_edit_learningunit_pedagogy"))
        self.current_ac = create_current_academic_year()
        self.ac_years_containers = GenerateAcademicYear(start_year=self.current_ac.year + 1,
                                                        end_year=self.current_ac.year + 5)
        self.current_luy = LearningUnitYearFactory(
            learning_container_year__academic_year=self.current_ac,
            academic_year=self.current_ac,
            acronym="LAGRO1000",
            subtype=FULL
        )
        self.luys = {self.current_ac.year: self.current_luy}
        self.luys.update(
            _duplicate_learningunityears(self.current_luy, academic_years=self.ac_years_containers.academic_years)
        )


class TestValidation(LearningUnitPedagogyContextMixin):
    def setUp(self):
        super().setUp()
        self.cms_translated_text = TranslatedTextFactory(
            entity=entity_name.LEARNING_UNIT_YEAR,
            reference=self.luys[self.current_ac.year].id,
            language='EN',
            text='Text random'
        )
        self.valid_form_data = _get_valid_cms_form_data(self.cms_translated_text)

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
        """In this test, we ensure that if we modify UE of N or N-... => The postponement is not done for CMS data"""
        form = LearningUnitPedagogyEditForm(self.valid_form_data)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        mock_update_or_create.assert_called_once_with(entity=self.cms_translated_text.entity,
                                                      reference=self.cms_translated_text.reference,
                                                      language=self.cms_translated_text.language,
                                                      text_label=self.cms_translated_text.text_label,
                                                      defaults={'text': self.cms_translated_text.text})

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
        form = LearningUnitPedagogyEditForm(data=_get_valid_cms_form_data(cms_pedagogy_future))
        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        # N+1 ===> N+6
        self.assertEqual(mock_update_or_create.call_count, 5)


class TestTeachingMaterialFormSet(LearningUnitPedagogyContextMixin):
    @patch('base.models.teaching_material.postpone_teaching_materials', side_effect=lambda *args: None)
    def test_save_without_postponement(self, mock_postpone_teaching_materials):
        """In this test, we ensure that if we modify UE of N or N-... => The postponement is not done for teaching
           materials"""
        TeachingMaterialFormset = teachingmaterialformset_factory(can_edit=True)
        teaching_materials = [
            TeachingMaterialFactory.build(learning_unit_year=self.current_luy),
            TeachingMaterialFactory.build(learning_unit_year=self.current_luy),
            TeachingMaterialFactory.build(learning_unit_year=self.current_luy)
        ]
        post_data = _get_valid_teaching_materials_formset_data(teaching_materials)
        teaching_material_formset = TeachingMaterialFormset(post_data, instance=self.current_luy,
                                                            form_kwargs={'person': self.person})
        self.assertTrue(teaching_material_formset.is_valid(), teaching_material_formset.errors)
        teaching_material_formset.save()
        self.assertFalse(mock_postpone_teaching_materials.called)

    @patch('base.models.teaching_material.postpone_teaching_materials', side_effect=lambda *args: None)
    def test_save_with_postponement(self, mock_postpone_teaching_materials):
        """In this test, we ensure that if we modify UE of N+1 or N+X => The postponement until the lastest UE"""
        luy_in_future = self.luys[self.current_ac.year + 1]
        TeachingMaterialFormset = teachingmaterialformset_factory(can_edit=True)
        teaching_materials = [
            TeachingMaterialFactory.build(learning_unit_year=luy_in_future)
        ]
        post_data = _get_valid_teaching_materials_formset_data(teaching_materials)
        teaching_material_formset = TeachingMaterialFormset(post_data, instance=luy_in_future,
                                                            form_kwargs={'person': self.person})
        self.assertTrue(teaching_material_formset.is_valid(), teaching_material_formset.errors)
        teaching_material_formset.save()
        self.assertTrue(mock_postpone_teaching_materials.called)


class TestSummaryModelForm(LearningUnitPedagogyContextMixin):
    @patch('base.forms.learning_unit_pedagogy.SummaryModelForm._postpone_pedagogy_data', side_effect=lambda *args: None)
    def test_save_without_postponement(self, mock_postpone_summary):
        post_data = _get_valid_summary_form_data(self.current_luy)
        form = SummaryModelForm(post_data, self.person, is_person_linked_to_entity=True, instance=self.current_luy)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertFalse(mock_postpone_summary.called)

    @patch('base.forms.learning_unit_pedagogy.SummaryModelForm._postpone_pedagogy_data', side_effect=lambda *args: None)
    def test_save_with_postponement(self, mock_postpone_summary):
        luy_in_future = self.luys[self.current_ac.year + 1]
        post_data = _get_valid_summary_form_data(luy_in_future)
        form = SummaryModelForm(post_data, self.person, is_person_linked_to_entity=True, instance=luy_in_future)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertTrue(mock_postpone_summary.called)

    @patch("cms.models.translated_text.update_or_create")
    def test_save_fr_bibliography_also_updates_en_bibliography(self, mock_update_or_create):
        """Ensure that if we modify bibliography in FR => bibliography in EN is updated with same text"""
        text_label_bibliography = TextLabelFactory(
            entity=entity_name.LEARNING_UNIT_YEAR,
            label='bibliography'
        )
        cms_translated_text_fr = TranslatedTextFactory(
            entity=entity_name.LEARNING_UNIT_YEAR,
            reference=self.luys[self.current_ac.year].id,
            language='fr-be',
            text_label=text_label_bibliography,
            text='Some random text'
        )
        valid_form_data_fr = _get_valid_cms_form_data(cms_translated_text_fr)

        form = LearningUnitPedagogyEditForm(valid_form_data_fr)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        for language in settings.LANGUAGES:
            mock_update_or_create.assert_any_call(
                entity=cms_translated_text_fr.entity,
                reference=cms_translated_text_fr.reference,
                language=language[0],
                text_label=cms_translated_text_fr.text_label,
                defaults={'text': cms_translated_text_fr.text}
            )


def _duplicate_learningunityears(luy_to_duplicate, academic_years):
    # Duplicate learning unit year with different academic year
    luys = {}
    for ac_year in academic_years:
        new_luy = copy(luy_to_duplicate)
        new_luy.pk = None
        new_luy.uuid = uuid.uuid4()
        new_luy.academic_year = ac_year
        new_luy.save()
        luys[ac_year.year] = new_luy
    return luys


def _get_valid_cms_form_data(cms_translated_text):
    """Valid data for form CMS form"""
    return {
        "trans_text": getattr(cms_translated_text, 'text'),
        "cms_id": getattr(cms_translated_text, 'id'),
        "reference": getattr(cms_translated_text, 'reference')
    }


def _get_valid_teaching_materials_formset_data(teaching_materials):
    """Valid formset data for teaching materials formset"""
    management_form = {
        'teachingmaterial_set-INITIAL_FORMS': 0,
        'teachingmaterial_set-MAX_NUM_FORMS': 10,
        'teachingmaterial_set-MIN_NUM_FORMS': 0,
        'teachingmaterial_set-TOTAL_FORMS': len(teaching_materials),
    }
    formset_data = {}
    for index, teaching_material in enumerate(teaching_materials):
        row_prefix = 'teachingmaterial_set-{}'.format(index)
        row_data = {
            '{}-id'.format(row_prefix): getattr(teaching_material, 'id') or '',
            '{}-learning_unit_year'.format(row_prefix): getattr(teaching_material, 'learning_unit_year_id') or '',
            '{}-title'.format(row_prefix): getattr(teaching_material, 'title') or '',
            '{}-DELETE'.format(row_prefix): ''
        }
        if getattr(teaching_material, 'mandatory', False):
            row_data['{}-mandatory'.format(row_prefix)] = 'on'
        formset_data.update(row_data)
    return dict(management_form, **formset_data)


def _get_valid_summary_form_data(luy):
    return {
        'summary_locked': luy.summary_locked,
        'mobility_modality' : luy.mobility_modality
    }
