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
import datetime
from base.forms.learning_unit.learning_unit_create_2 import FullForm
from base.models.academic_year import AcademicYear
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.business.learning_units import GenerateContainer
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from django.contrib.auth.models import Group
from django.test import TestCase, RequestFactory
from django.utils.translation import ugettext_lazy as _

from base.forms.learning_unit.learning_unit_create import LearningUnitFormContainer, LearningUnitYearModelForm, \
    LearningUnitModelForm, EntityContainerFormset, LearningContainerYearModelForm, LearningUnitYearPartimModelForm, \
    LearningContainerModelForm
from base.models.enums import learning_container_year_types
from base.models.enums import learning_unit_year_subtypes
from base.models.person import CENTRAL_MANAGER_GROUP, FACULTY_MANAGER_GROUP
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.campus import CampusFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory, LearningUnitYearFakerFactory
from base.tests.factories.person import PersonFactory
from reference.tests.factories.language import LanguageFactory


def _instanciate_form(default_ac_year=None, post_data=None, instance=None):
    person = PersonFactory()
    return FullForm(post_data, person, instance=instance, default_ac_year=default_ac_year)


class TestFullFormInit(TestCase):
    """Unit tests for FullForm.__init__()"""

    def setUp(self):
        self.initial_language = LanguageFactory(code='FR')
        self.initial_campus = CampusFactory(name='Louvain-la-Neuve')
        self.academic_year = create_current_academic_year()
        container_year = LearningContainerYearFactory.build(academic_year=self.academic_year)
        self.post_data = get_valid_form_data(LearningUnitYearFactory.build(academic_year=self.academic_year,
                                                                           learning_container_year=container_year))

    def test_subtype_is_full(self):
        form = _instanciate_form(instance=LearningUnitYearFactory())
        self.assertEqual(form.subtype, learning_unit_year_subtypes.FULL)

    def test_wrong_instance_arg(self):
        wrong_instance = LearningUnitFactory()
        with self.assertRaises(AttributeError):
            _instanciate_form(instance=wrong_instance)

    def test_academic_year_value_case_instance_arg_given(self):
        learning_unit_year_instance = LearningUnitYearFactory()
        form = _instanciate_form(instance=learning_unit_year_instance)
        self.assertEqual(form.academic_year, learning_unit_year_instance.academic_year)

    def test_academic_year_value_case_default_academic_year_arg_given(self):
        academic_year = AcademicYearFactory()
        form = _instanciate_form(default_ac_year=academic_year)
        self.assertEqual(form.academic_year, academic_year)

    def test_academic_year_value_case_default_academic_year_and_instance_args_given(self):
        academic_year = AcademicYearFactory()
        learning_unit_year_instance = LearningUnitYearFactory()
        form = _instanciate_form(default_ac_year=academic_year, instance=learning_unit_year_instance)
        self.assertEqual(form.academic_year, learning_unit_year_instance.academic_year)

    def test_model_form_instances_case_creation(self):
        form = _instanciate_form(post_data=self.post_data, default_ac_year=self.academic_year)
        for cls in FullForm.forms:
            self.assertIsInstance(form.form_instances[cls], cls)

    def test_initial_values_of_form_instances_case_creation(self):
        full_form = _instanciate_form(post_data=self.post_data, default_ac_year=self.academic_year)
        expected_initials = {
            LearningUnitYearModelForm: {
                'status': True, 'academic_year': self.academic_year, 'subtype': learning_unit_year_subtypes.FULL
            },
            LearningContainerYearModelForm: {
                'campus': self.initial_campus,
                'language': self.initial_language,
            }
        }
        for form_class, initial in expected_initials.items():
            self.assertEqual(full_form.form_instances[form_class].initial, initial)

    def test_model_form_instances_case_update(self):
        now = datetime.datetime.now()
        learn_unit_structure = GenerateContainer(now.year, now.year)
        learn_unit_year = LearningUnitYear.objects.get(learning_unit=learn_unit_structure.learning_unit_full,
                                                       academic_year=AcademicYear.objects.get(year=now.year))
        form = _instanciate_form(post_data=self.post_data, instance=learn_unit_year)

        self.assertEqual(form.form_instances[LearningUnitModelForm].instance, learn_unit_year.learning_unit)
        self.assertEqual(form.form_instances[LearningContainerModelForm].instance, learn_unit_year.learning_container_year.learning_container)
        self.assertEqual(form.form_instances[LearningUnitYearModelForm].instance, learn_unit_year)
        self.assertEqual(form.form_instances[LearningContainerYearModelForm].instance, learn_unit_year.learning_container_year)
        # TODO :: to implement
        # for entity_form in enumerate(form.form_instances[LearningUnitModelForm].forms):
        #     self.assertEqual()


class TestFullFormIsValid(TestCase):
    """Unit tests for is_valid() """
    def setUp(self):
        self.initial_language = LanguageFactory(code='FR')
        self.initial_campus = CampusFactory(name='Louvain-la-Neuve')
        self.academic_year = create_current_academic_year()
        container_year = LearningContainerYearFactory.build(academic_year=self.academic_year)
        self.post_data = get_valid_form_data(LearningUnitYearFactory.build(academic_year=self.academic_year,
                                                                           learning_container_year=container_year))

    def _assert_equal_values(self, obj, dictionnary, fields_to_validate):
        for field in fields_to_validate:
            self.assertEqual(getattr(obj, field), dictionnary[field], msg='Error field = {}'.format(field))

    def test_creation_case_correct_post_data(self):
        form = _instanciate_form(post_data=self.post_data, default_ac_year=self.academic_year)
        form.is_valid()
        self._test_learning_unit_model_form_instance(form)
        self._test_learning_unit_year_model_form_instance(form)
        self._test_learning_container_model_form_instance(form)
        self._test_learning_container_year_model_form_instance(form)

    def _test_learning_unit_model_form_instance(self, full_form):
        form_instance = full_form.form_instances[LearningUnitModelForm]
        fields_to_validate = ['faculty_remark', 'other_remark', 'periodicity']
        self._assert_equal_values(form_instance.instance, self.post_data, fields_to_validate)

    def _test_learning_container_model_form_instance(self, full_form):
        self.assertIn(LearningContainerModelForm, full_form.form_instances)

    def _test_learning_unit_year_model_form_instance(self, full_form):
        form_instance = full_form.form_instances[LearningUnitYearModelForm]
        fields_to_validate = ['acronym', 'specific_title', 'specific_title_english', 'credits',
                              'session', 'quadrimester', 'status', 'internship_subtype', 'attribution_procedure', 'subtype',]
        self._assert_equal_values(form_instance.instance, self.post_data, fields_to_validate)
        self.assertEqual(form_instance.instance.academic_year.id, self.post_data['academic_year'])

    def _test_learning_container_year_model_form_instance(self, full_form):
        form_instance = full_form.form_instances[LearningContainerYearModelForm]
        fields_to_validate = ['container_type', 'common_title', 'common_title_english',
                              'type_declaration_vacant', 'team', 'is_vacant']
        self._assert_equal_values(form_instance.instance, self.post_data, fields_to_validate)

    def _test_entity_container_model_formset_instance(self, full_form):
        self.assertIn(EntityContainerFormset, full_form.form_instances)

    def test_creation_case_wrong_learning_unit_data(self):
        """Need to mock LearningUnitModelForm.is_valid"""
        from base.forms.learning_unit.learning_unit_create import LearningUnitModelForm as LUModelForm
        LUModelForm.is_valid = lambda *args, **kwargs: False
        form = _instanciate_form(post_data=self.post_data, default_ac_year=self.academic_year)
        self.assertFalse(form.is_valid())

    def test_creation_case_wrong_learning_unit_year_data(self):
        """Need to mock LearningUnitYearModelForm.is_valid"""
        pass

    def test_creation_case_wrong_learning_container_year_data(self):
        """Need to mock LearningContainerYearModelForm.is_valid"""
        pass

    def test_creation_case_wrong_entity_container_year_data(self):
        """Need to mock LearningUnitModelForm.is_valid"""
        pass

    def test_update_case_correct_data(self):
        """need to assert assert form.is_valid is True"""
        pass

    def test_update_case_wrong_learning_unit_data(self):
        # réutiliser mêmes tests qu ci-dessus mais en passant un form avec une instance
        pass



#
# class TestLearningUnitFormContainer(TestCase):
#     def setUp(self):
#         self.language = LanguageFactory(code="FR", name='French')
#         self.campus = CampusFactory()
#         self.person = PersonFactory()
#         self.academic_year = create_current_academic_year()
#         self.learning_unit_year_full = LearningUnitYearFactory(
#             academic_year=self.academic_year,
#             subtype=learning_unit_year_subtypes.FULL,
#             learning_container_year__academic_year=self.academic_year,
#             learning_container_year__container_type=learning_container_year_types.COURSE
#         )
#
#     def test_is_subtype_full(self):
#         form = LearningUnitFormContainer(data={}, person=self.person, default_ac_year=self.academic_year)
#         self.assertEqual(form.subtype, learning_unit_year_subtypes.FULL)
#
#     def test_get_context_subtype_full(self):
#         form = LearningUnitFormContainer(data={}, person=self.person, default_ac_year=self.academic_year)
#         context = form.get_context()
#         self.assertTrue(context['subtype'])
#         self.assertEqual(context['subtype'], learning_unit_year_subtypes.FULL)
#         self.assertTrue(context['learning_unit_year_form'])
#         self.assertIsInstance(context['learning_unit_year_form'], LearningUnitYearModelForm)
#         self.assertTrue(context['learning_unit_form'])
#         self.assertIsInstance(context['learning_unit_form'], LearningUnitModelForm)
#         self.assertTrue(context['learning_container_year_form'])
#         self.assertIsInstance(context['learning_container_year_form'], LearningContainerYearModelForm)
#         self.assertTrue(context['entity_container_form'])
#         self.assertIsInstance(context['entity_container_form'], EntityContainerFormset)
#
#     def test_is_subtype_partim(self):
#         form = LearningUnitFormContainer(data={}, person=self.person, default_ac_year=self.academic_year,
#                                          learning_unit_year_full=self.learning_unit_year_full)
#         self.assertEqual(form.subtype, learning_unit_year_subtypes.PARTIM)
#
#     def test_get_context_subtype_partim(self):
#         form = LearningUnitFormContainer(data={}, person=self.person, default_ac_year=self.academic_year,
#                                          learning_unit_year_full=self.learning_unit_year_full)
#         context = form.get_context()
#         self.assertTrue(context['subtype'])
#         self.assertEqual(context['subtype'], learning_unit_year_subtypes.PARTIM)
#         self.assertTrue(context['learning_unit_year_form'])
#         self.assertIsInstance(context['learning_unit_year_form'], LearningUnitYearPartimModelForm)
#
#     def test_check_disable_field_subtype_partim(self):
#         """This test will ensure that all expected field are disabled when user create PARTIM"""
#         form = LearningUnitFormContainer(data={}, person=self.person, default_ac_year=self.academic_year,
#                                          learning_unit_year_full=self.learning_unit_year_full)
#         all_fields = form.get_all_fields()
#         self.assertIsInstance(all_fields, dict)
#
#         expected_fields_disabled = {
#             'common_title', 'common_title_english', 'requirement_entity',
#             'allocation_entity', 'language', 'periodicity', 'campus', 'academic_year', 'container_type',
#             'internship_subtype','additional_requirement_entity_1', 'additional_requirement_entity_2'
#         }
#         self.assertTrue(all(getattr(field, 'disabled', False) == (name in expected_fields_disabled)
#                             for name, field in all_fields.items()))
#
#     def test_get_inherit_luy_value_from_full(self):
#         form = LearningUnitFormContainer(data={}, person=self.person, default_ac_year=self.academic_year,
#                                          learning_unit_year_full=self.learning_unit_year_full)
#         expected_inherit_luy_field_names = {
#             'acronym', 'academic_year', 'specific_title', 'specific_title_english',
#             'credits', 'session', 'quadrimester', 'status', 'internship_subtype', 'attribution_procedure'
#         }
#         inherit_field = form._get_inherit_luy_value_from_full()
#         self.assertFalse(expected_inherit_luy_field_names ^ set(inherit_field.keys()))
#
#         self.assertEqual(inherit_field.pop('academic_year', None), self.learning_unit_year_full.academic_year.id)
#         self.assertTrue(all(getattr(self.learning_unit_year_full, field_name) == value
#                             for field_name, value in inherit_field.items()))
#
#     def test_get_inherit_lu_value_from_full(self):
#         form = LearningUnitFormContainer(data={}, person=self.person, default_ac_year=self.academic_year,
#                                          learning_unit_year_full=self.learning_unit_year_full)
#         expected_inherit_lu_field_names = {'periodicity'}
#         inherit_field = form._get_inherit_lu_value_from_full()
#         self.assertFalse(expected_inherit_lu_field_names ^ set(inherit_field.keys()))
#         self.assertEqual(inherit_field['periodicity'], self.learning_unit_year_full.learning_unit.periodicity)
#
#     def test_create_learning_unit_year_full_missing_data(self):
#         new_lunit_year = LearningUnitYearFactory.build(
#             academic_year=self.academic_year,
#             learning_container_year__academic_year=self.academic_year,
#             learning_container_year__campus=self.campus,
#             learning_container_year__language=self.language,
#             learning_container_year__container_type=learning_container_year_types.COURSE
#         )
#         valid_form_data = get_valid_form_data_full_luy(new_lunit_year)
#         pass
#

def get_valid_form_data(learning_unit_year):
    return {
        # Learning unit year data model form
        'acronym': learning_unit_year.acronym,
        'acronym_0': learning_unit_year.acronym[0],
        'acronym_1': learning_unit_year.acronym[1:],
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
        'periodicity': learning_unit_year.learning_unit.periodicity,
        'faculty_remark': learning_unit_year.learning_unit.faculty_remark,
        'other_remark': learning_unit_year.learning_unit.other_remark,

        # Learning container year data model form
        'campus': learning_unit_year.learning_container_year.campus,
        'language': learning_unit_year.learning_container_year.language,
        'common_title': learning_unit_year.learning_container_year.common_title,
        'common_title_english': learning_unit_year.learning_container_year.common_title_english,
        'container_type': learning_unit_year.learning_container_year.container_type,
        'type_declaration_vacant': learning_unit_year.learning_container_year.type_declaration_vacant,
        'team': learning_unit_year.learning_container_year.team,
        'is_vacant': learning_unit_year.learning_container_year.is_vacant,

        'entitycontaineryear_set-0-entity': '',
        'entitycontaineryear_set-1-entity': '',
        'entitycontaineryear_set-2-entity': '',
        'entitycontaineryear_set-INITIAL_FORMS': '0',
        'entitycontaineryear_set-MAX_NUM_FORMS': '4',
        'entitycontaineryear_set-MIN_NUM_FORMS': '3',
        'entitycontaineryear_set-TOTAL_FORMS': '4',
    }