##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from django import forms
from django.contrib.auth.models import Group
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from base.forms.learning_unit.learning_unit_create import LearningUnitYearModelForm
from base.forms.utils.acronym_field import PartimAcronymField, AcronymField
from base.models.enums.learning_unit_year_subtypes import FULL, PARTIM
from base.models.person import CENTRAL_MANAGER_GROUP, FACULTY_MANAGER_GROUP
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.learning_container import LearningContainerFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory


class TestLearningUnitYearModelFormInit(TestCase):
    """Tests LearningUnitYearModelForm.__init__()"""
    def setUp(self):
        self.central_manager = PersonFactory()
        self.central_manager.user.groups.add(Group.objects.get(name=CENTRAL_MANAGER_GROUP))
        self.faculty_manager = PersonFactory()
        self.faculty_manager.user.groups.add(Group.objects.get(name=FACULTY_MANAGER_GROUP))

    def test_internship_subtype_removed_when_user_is_faculty_manager(self):

        self.form = LearningUnitYearModelForm(data=None, person=self.central_manager, subtype=FULL)
        self.assertIsInstance(self.form.fields.get('internship_subtype'), forms.TypedChoiceField)

        self.form = LearningUnitYearModelForm(data=None, person=self.faculty_manager, subtype=FULL)
        self.assertIsNone(self.form.fields.get('internship_subtype'))

    def test_acronym_field_case_partim(self):
        self.form = LearningUnitYearModelForm(data=None, person=self.central_manager, subtype=PARTIM)
        self.assertIsInstance(self.form.fields.get('acronym'), PartimAcronymField, "should assert field is PartimAcronymField")

    def test_acronym_field_case_full(self):
        self.form = LearningUnitYearModelForm(data=None, person=self.central_manager, subtype=FULL)
        self.assertIsInstance(self.form.fields.get('acronym'), AcronymField, "should assert field is AcronymField")

    def test_label_specific_title_case_partim(self):
        self.form = LearningUnitYearModelForm(data=None, person=self.central_manager, subtype=PARTIM)
        self.assertEqual(self.form.fields['specific_title'].label, _('official_title_proper_to_partim'))
        self.assertEqual(self.form.fields['specific_title_english'].label, _('official_english_title_proper_to_partim'))

    def test_case_update_academic_year_is_disabled(self):
        self.form = LearningUnitYearModelForm(data=None, person=self.central_manager, subtype=PARTIM,
                                              instance=LearningUnitYearFactory())
        self.assertTrue(self.form.fields['academic_year'].disabled)


# TODO :: unit tests on AcronymField et PartimAcronymField

class TestLearningUnitYearModelFormSave(TestCase):
    """Tests LearningUnitYearModelForm.save()"""

    def setUp(self):
        self.central_manager = PersonFactory()
        self.central_manager.user.groups.add(Group.objects.get(name=CENTRAL_MANAGER_GROUP))
        self.faculty_manager = PersonFactory()
        self.faculty_manager.user.groups.add(Group.objects.get(name=FACULTY_MANAGER_GROUP))

        self.learning_container = LearningContainerFactory()
        self.learning_unit = LearningUnitFactory(learning_container=self.learning_container)
        self.learning_container_year = LearningContainerYearFactory(learning_container=self.learning_container)
        self.form = LearningUnitYearModelForm(data=None, person=self.central_manager, subtype=FULL)
        self.learning_unit_year_to_update = LearningUnitYearFactory(
            learning_unit=self.learning_unit, learning_container_year=self.learning_container_year)

        self.current_academic_year = create_current_academic_year()
        self.post_data = {
            'acronym_0': 'L',
            'acronym_1': 'OSIS9001',
            'academic_year': self.current_academic_year.id,
            'specific_title': 'The hobbit ',
            'specific_title_english': 'An Unexpected Journey',
            'credits': 3,
            'session': 3,
            'quadrimester': 'Q1',
            'internship_subtype': '',
            'attribution_procedure': ''
        }

    def test_case_missing_required_learning_container_year_kwarg(self):
        with self.assertRaises(KeyError):
            self.form.save(learning_unit=self.learning_unit, entity_container_years=[])

    def test_case_missing_required_learning_unit_kwarg(self):
        with self.assertRaises(KeyError):
            self.form.save(learning_container_year=self.learning_container_year, entity_container_years=[])

    def test_case_missing_required_entity_container_years_kwarg(self):
        with self.assertRaises(KeyError):
            self.form.save(learning_container_year=self.learning_container_year, learning_unit=self.learning_unit)

    def test_post_data_correctly_saved_case_creation(self):
        "should assert get_attr(learning_unit_year_created, field) for field in fields_to_check are the same value than post_data[field]"
        fields_to_check = ['academic_year', 'acronym', 'specific_title', 'specific_title_english', 'credits',
                           'session', 'quadrimester', 'status', 'internship_subtype', 'attribution_procedure']

        form = LearningUnitYearModelForm(data=self.post_data, person=self.central_manager, subtype=FULL)
        self.assertTrue(form.is_valid(), form.errors)
        # TODO
        luy = self.form.save(learning_container_year=self.learning_container_year, learning_unit=self.learning_unit,
                             entity_container_years=[])

    def test_components_are_correctly_saved_when_creation_of_container_type_master_thesis(self):
        "case container_type = MASTER_THESIS and "
        self._assert_2_components_created()
        self._assert_default_acronyms_are_correctly_set()
        self._assert_learning_unit_components_correctly_created()
        pass

    def _assert_2_components_created(self):
        "should assert 2 components are created (1 TP - 1 LECTURING)"
        pass

    def _assert_default_acronyms_are_correctly_set(self):
        " acronyms should be ='CM1' and 'TP1'"
        pass

    def _assert_learning_unit_components_correctly_created(self):
        "Should assert 1 learning_unit_component is created by component"

    def test_components_are_correctly_saved_when_creation_of_container_type_other_individual(self):
        "should assert 1 only component of type=None is created with acronym 'NT1'"
        self._assert_1_component_type_none_is_created()
        self._assert_default_acronym_is_NT1()
        self._assert_1_learning_unit_component_correctly_saved()
        pass

    def _assert_1_component_type_none_is_created(self):
        pass

    def _assert_default_acronym_is_NT1(self):
        pass

    def _assert_1_learning_unit_component_correctly_saved(self):
        pass

    # def test_entity_components_year_correctly_saved_when_
    #
    #
    # def test_case_update_post_data_correctly_saved(self):
    #     pass
    #
    # def test_case_creation_


