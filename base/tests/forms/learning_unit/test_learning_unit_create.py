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
from django.contrib.auth.models import Group
from django.test import TestCase, RequestFactory
from django.utils.translation import ugettext_lazy as _

from base.forms.learning_unit.learning_unit_create import LearningUnitFormContainer, LearningUnitYearModelForm, \
    LearningUnitModelForm, EntityContainerFormset, LearningContainerYearModelForm, LearningUnitYearPartimModelForm
from base.models.enums import learning_container_year_types
from base.models.enums import learning_unit_year_subtypes
from base.models.person import CENTRAL_MANAGER_GROUP, FACULTY_MANAGER_GROUP
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.campus import CampusFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory
from reference.tests.factories.language import LanguageFactory


class TestLearningUnitYearModelForm(TestCase):
    def setUp(self):
        pass

    def test_internship_subtype_removed_when_user_is_faculty_manager(self):
        pass

    def test_subtype_widget_is_hidden_input(self):
        """Subtype must be present because not considered in POST_DATA if not present in fields
            + prevent use default value of model field"""
        pass


class TestLearningUnitFormContainer(TestCase):
    def setUp(self):
        self.language = LanguageFactory(code="FR", name='French')
        self.campus = CampusFactory()
        self.person = PersonFactory()
        self.academic_year = create_current_academic_year()
        self.learning_unit_year_full = LearningUnitYearFactory(
            academic_year=self.academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_container_year__academic_year=self.academic_year,
            learning_container_year__container_type=learning_container_year_types.COURSE
        )

    def test_is_subtype_full(self):
        form = LearningUnitFormContainer(data={}, person=self.person, default_ac_year=self.academic_year)
        self.assertEqual(form.subtype, learning_unit_year_subtypes.FULL)

    def test_get_context_subtype_full(self):
        form = LearningUnitFormContainer(data={}, person=self.person, default_ac_year=self.academic_year)
        context = form.get_context()
        self.assertTrue(context['subtype'])
        self.assertEqual(context['subtype'], learning_unit_year_subtypes.FULL)
        self.assertTrue(context['learning_unit_year_form'])
        self.assertIsInstance(context['learning_unit_year_form'], LearningUnitYearModelForm)
        self.assertTrue(context['learning_unit_form'])
        self.assertIsInstance(context['learning_unit_form'], LearningUnitModelForm)
        self.assertTrue(context['learning_container_year_form'])
        self.assertIsInstance(context['learning_container_year_form'], LearningContainerYearModelForm)
        self.assertTrue(context['entity_container_form'])
        self.assertIsInstance(context['entity_container_form'], EntityContainerFormset)

    def test_is_subtype_partim(self):
        form = LearningUnitFormContainer(data={}, person=self.person, default_ac_year=self.academic_year,
                                         learning_unit_year_full=self.learning_unit_year_full)
        self.assertEqual(form.subtype, learning_unit_year_subtypes.PARTIM)

    def test_get_context_subtype_partim(self):
        form = LearningUnitFormContainer(data={}, person=self.person, default_ac_year=self.academic_year,
                                         learning_unit_year_full=self.learning_unit_year_full)
        context = form.get_context()
        self.assertTrue(context['subtype'])
        self.assertEqual(context['subtype'], learning_unit_year_subtypes.PARTIM)
        self.assertTrue(context['learning_unit_year_form'])
        self.assertIsInstance(context['learning_unit_year_form'], LearningUnitYearPartimModelForm)

    def test_check_disable_field_subtype_partim(self):
        """This test will ensure that all expected field are disabled when user create PARTIM"""
        form = LearningUnitFormContainer(data={}, person=self.person, default_ac_year=self.academic_year,
                                         learning_unit_year_full=self.learning_unit_year_full)
        all_fields = form.get_all_fields()
        self.assertIsInstance(all_fields, dict)

        expected_fields_disabled = {
            'common_title', 'common_title_english', 'requirement_entity',
            'allocation_entity', 'language', 'periodicity', 'campus', 'academic_year', 'container_type',
            'internship_subtype','additional_requirement_entity_1', 'additional_requirement_entity_2'
        }
        self.assertTrue(all(getattr(field, 'disabled', False) == (name in expected_fields_disabled)
                            for name, field in all_fields.items()))

    def test_get_inherit_luy_value_from_full(self):
        form = LearningUnitFormContainer(data={}, person=self.person, default_ac_year=self.academic_year,
                                         learning_unit_year_full=self.learning_unit_year_full)
        expected_inherit_luy_field_names = {
            'acronym', 'academic_year', 'specific_title', 'specific_title_english',
            'credits', 'session', 'quadrimester', 'status', 'internship_subtype', 'attribution_procedure'
        }
        inherit_field = form._get_inherit_luy_value_from_full()
        self.assertFalse(expected_inherit_luy_field_names ^ set(inherit_field.keys()))

        self.assertEqual(inherit_field.pop('academic_year', None), self.learning_unit_year_full.academic_year.id)
        self.assertTrue(all(getattr(self.learning_unit_year_full, field_name) == value
                            for field_name, value in inherit_field.items()))

    def test_get_inherit_lu_value_from_full(self):
        form = LearningUnitFormContainer(data={}, person=self.person, default_ac_year=self.academic_year,
                                         learning_unit_year_full=self.learning_unit_year_full)
        expected_inherit_lu_field_names = {'periodicity'}
        inherit_field = form._get_inherit_lu_value_from_full()
        self.assertFalse(expected_inherit_lu_field_names ^ set(inherit_field.keys()))
        self.assertEqual(inherit_field['periodicity'], self.learning_unit_year_full.learning_unit.periodicity)

    def test_create_learning_unit_year_full_missing_data(self):
        new_lunit_year = LearningUnitYearFactory.build(
            academic_year=self.academic_year,
            learning_container_year__academic_year=self.academic_year,
            learning_container_year__campus=self.campus,
            learning_container_year__language=self.language,
            learning_container_year__container_type=learning_container_year_types.COURSE
        )
        valid_form_data = get_valid_form_data_full_luy(new_lunit_year)
        pass

def get_valid_form_data_full_luy(learning_unit_year):
    return {
        # Learning unit year data model form
        'acronym': learning_unit_year.acronym,
        'subtype': learning_unit_year.subtype,
        'academic_year': learning_unit_year.academic_year.id,
        'specific_title': learning_unit_year.specific_title,
        'specific_title_english': learning_unit_year.specific_title_english,
        'credits': learning_unit_year.credits,
        'session': learning_unit_year.session,
        'quadrimester': learning_unit_year.quadrimester,
        'status': learning_unit_year.status,
        'internship_subtype': learning_unit_year.internship_subtype,
        'attribution_procedure': learning_unit_year.attribution_procedure,
        # Learning unit data model form
        'periocidity': learning_unit_year.learning_unit.periodicity,
        # Learning container year data model form
        'campus': learning_unit_year.learning_container_year.campus,
        'language': learning_unit_year.learning_container_year.language,
        'common_title': learning_unit_year.learning_container_year.common_title,
        'common_title_english': learning_unit_year.learning_container_year.common_title_english,
        'container_type': learning_unit_year.learning_container_year.container_type,
        'type_declaration_vacant': learning_unit_year.learning_container_year.type_declaration_vacant,
        'team': learning_unit_year.learning_container_year.team ,
        'is_vacant': learning_unit_year.learning_container_year.is_vacant
    }