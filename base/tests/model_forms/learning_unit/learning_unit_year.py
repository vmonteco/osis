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
from django.test import TestCase


class TestLearningUnitYearModelFormInit(TestCase):
    """Tests LearningUnitYearModelForm.__init__()"""
    def setUp(self):
        pass

    def test_case_missing_person_kwarg(self):
        pass

    def test_case_missing_subtype_kwargs(self):
        pass

    def test_internship_subtype_removed_when_user_is_faculty_manager(self):
        pass

    def test_acronym_field_case_partim(self):
        "should assert field is PartimAcronymField"
        pass

    def test_acronym_field_case_full(self):
        "should assert field is AcronymField"

    def test_label_specific_title_case_partim(self):
        'should assert specific_title label correctly translated "proper to partim" '
        pass

    def test_label_common_title_case_partim(self):
        'should assert common_title label correctly translated "proper to partim" '
        pass

    def test_case_update_academic_year_is_disabled(self):
        pass

    def test_subtype_widget_is_hidden_input(self):
        """Subtype must be present because not considered in POST_DATA if not present in fields
            + prevent use default value of model field"""
        pass

# TODO :: unit tests on AcronymField et PartimAcronymField

class TestLearningUnitYearModelFormSave(TestCase):
    """Tests LearningUnitYearModelForm.save()"""
    def setUp(self):
        pass

    def test_case_missing_required_learning_container_year_kwarg(self):
        pass

    def test_case_missing_required_learning_unit_kwarg(self):
        pass

    def test_case_missing_required_subtype_kwarg(self):
        pass

    def test_case_missing_required_entity_container_years_kwarg(self):
        pass

    def test_learning_container_year_not_updated(self):
        "if instance is given (in case of update), the Modelform can't update the instance.learning_container_year value from post_data"
        pass

    def test_learning_unit_not_updated(self):
        "if instance is given (in case of update), the Modelform can't update the instance.learning_unit value from post_data"
        pass

    def test_subtype_not_updated(self):
        "if instance is given (in case of update), the Modelform can't update the instance.subtype value from post_data"
        pass

    def test_post_data_correctly_saved_case_creation(self):
        "should assert get_attr(learning_unit_year_created, field) for field in fields_to_check are the same value than post_data[field]"
        fields_to_check = ['academic_year', 'acronym', 'specific_title', 'specific_title_english', 'credits',
                           'session', 'quadrimester', 'status', 'internship_subtype', 'attribution_procedure']
        pass

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


