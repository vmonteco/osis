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
from django.http import QueryDict

from base.forms.learning_unit.learning_unit_create_2 import PartimForm
from base.forms.utils import acronym_field
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.business.learning_units import GenerateContainer
from base.tests.factories.learning_unit import LearningUnitFactory

from django.test import TestCase

from base.forms.learning_unit.learning_unit_create import LearningUnitYearModelForm, \
    LearningUnitModelForm, EntityContainerFormset, LearningContainerYearModelForm, LearningContainerModelForm
from base.models.enums import learning_container_year_types
from base.models.enums import learning_unit_year_subtypes
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory


def _instanciate_form(learning_unit_year_full, post_data=None, instance=None):
    person = PersonFactory()
    return PartimForm(post_data, person, learning_unit_year_full, instance=instance)

FULL_ACRONYM='LBIR1200'
SUBDIVISION_ACRONYM='A'
class TestPartimFormInit(TestCase):
    """Unit tests for PartimForm.__init__()"""
    def setUp(self):
        self.academic_year = create_current_academic_year()
        self.learning_unit_year_full = LearningUnitYearFactory(
            acronym=FULL_ACRONYM,
            academic_year=self.academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_container_year__academic_year=self.academic_year,
            learning_container_year__container_type=learning_container_year_types.COURSE
        )

    def test_subtype_is_partim(self):
        form = _instanciate_form(self.learning_unit_year_full)
        self.assertEqual(form.subtype, learning_unit_year_subtypes.PARTIM)

    def test_wrong_learning_unit_year_full_args(self):
        wrong_luy_full = LearningUnitFactory()
        with self.assertRaises(AttributeError):
            _instanciate_form(learning_unit_year_full=wrong_luy_full)

    def test_wrong_subtype_learning_unit_year_full_args(self):
        self.learning_unit_year_full.subtype = learning_unit_year_subtypes.PARTIM
        with self.assertRaises(AttributeError):
            _instanciate_form(learning_unit_year_full=self.learning_unit_year_full)

    def test_wrong_instance_args(self):
        wrong_instance = LearningUnitFactory()
        with self.assertRaises(AttributeError):
            _instanciate_form(learning_unit_year_full=self.learning_unit_year_full,
                              instance=wrong_instance)

    def test_model_form_instances_case_creation(self):
        form = _instanciate_form(self.learning_unit_year_full)
        for cls in PartimForm.forms:
            self.assertIsInstance(form.form_instances[cls], cls)

    def test_inherit_initial_values(self):
        """This test will check if field are pre-full in by value of full learning unit year"""
        expected_initials = {
            LearningUnitModelForm: {
                'periodicity': self.learning_unit_year_full.learning_unit.periodicity
            },
            LearningUnitYearModelForm: {
                'acronym': self.learning_unit_year_full.acronym,
                'acronym_0': 'L',  # Multiwidget decomposition
                'acronym_1': 'BIR1200',
                'acronym_2': '',
                'academic_year': self.learning_unit_year_full.academic_year.id,
                'internship_subtype': self.learning_unit_year_full.internship_subtype,
                'attribution_procedure': self.learning_unit_year_full.attribution_procedure,
                'subtype': learning_unit_year_subtypes.PARTIM,  # Creation of partim
                'credits': self.learning_unit_year_full.credits,
                'session': self.learning_unit_year_full.session,
                'quadrimester': self.learning_unit_year_full.quadrimester,
                'status': self.learning_unit_year_full.status,
                'specific_title': self.learning_unit_year_full.specific_title,
                'specific_title_english': self.learning_unit_year_full.specific_title_english
            }
        }
        partim_form = _instanciate_form(self.learning_unit_year_full)
        for form_class, initial in expected_initials.items():
            self.assertEqual(partim_form.form_instances[form_class].initial, initial)

    def test_disabled_fields(self):
        """This function will check if fields is disabled"""
        partim_form = _instanciate_form(self.learning_unit_year_full)
        expected_disabled_fields = {
            'common_title', 'common_title_english',
            'requirement_entity', 'allocation_entity',
            'language', 'periodicity', 'campus',
            'academic_year', 'container_type', 'internship_subtype',
            'additional_requirement_entity_1', 'additional_requirement_entity_2'
        }
        all_fields = partim_form.get_all_fields().items()
        self.assertTrue(all(field.disabled == (field_name in expected_disabled_fields)
                            for field_name, field in all_fields))

class TestPartimFormIsValid(TestCase):
    """Unit tests for is_valid() """
    def setUp(self):
        self.current_academic_year = create_current_academic_year()

        # Creation of a LearingContainerYear and all related models
        self.learn_unit_structure = GenerateContainer(self.current_academic_year.year, self.current_academic_year.year)
        # Build in Generated Container [first index = start Generate Container ]
        self.generated_container_year = self.learn_unit_structure.generated_container_years[0]

        # Update Full learning unit year acronym
        self.learning_unit_year_full = LearningUnitYear.objects.get(
            learning_unit=self.learn_unit_structure.learning_unit_full,
            academic_year=self.current_academic_year
        )
        self.learning_unit_year_full.acronym = FULL_ACRONYM
        self.learning_unit_year_full.save()

        # Update Partim learning unit year acronym
        self.learning_unit_year_partim = LearningUnitYear.objects.get(
            learning_unit=self.learn_unit_structure.learning_unit_partim,
            academic_year=self.current_academic_year
        )
        self.learning_unit_year_full.acronym = FULL_ACRONYM + SUBDIVISION_ACRONYM
        self.learning_unit_year_full.save()

    def _assert_equal_values(self, obj, dictionnary, fields_to_validate):
        for field in fields_to_validate:
            self.assertEqual(getattr(obj, field), dictionnary[field], msg='Error field = {}'.format(field))

    def test_creation_case_correct_post_data(self):
        a_new_learning_unit_partim = LearningUnitYearFactory.build(
            academic_year=self.current_academic_year,
            acronym=FULL_ACRONYM + 'B',
            subtype=learning_unit_year_subtypes.PARTIM
        )
        post_data = get_valid_form_data(a_new_learning_unit_partim)
        form = _instanciate_form(self.learning_unit_year_full, post_data=post_data)
        # The form should be valid
        self.assertTrue(form.is_valid())
        # In partim, we can only modify LearningUnitYearModelForm / LearningUnitModelForm
        self._test_learning_unit_model_form_instance(form, post_data)
        self._test_learning_unit_year_model_form_instance(form, post_data)
        # Inherit instance from learning unit year full
        self._test_learning_container_model_form_instance(form)
        self._test_learning_container_year_model_form_instance(form)
        self._test_entity_container_model_formset_instance(form)

    def _test_learning_unit_model_form_instance(self, partim_form, post_data):
        form_instance = partim_form.form_instances[LearningUnitModelForm]
        fields_to_validate = ['faculty_remark', 'other_remark', 'periodicity']
        self._assert_equal_values(form_instance.instance, post_data, fields_to_validate)

    def _test_learning_unit_year_model_form_instance(self, partim_form, post_data):
        form_instance = partim_form.form_instances[LearningUnitYearModelForm]
        fields_to_validate = ['specific_title', 'specific_title_english', 'credits',
                              'session', 'quadrimester', 'status', 'subtype', ]
        self._assert_equal_values(form_instance.instance, post_data, fields_to_validate)
        self.assertEqual(form_instance.instance.acronym, FULL_ACRONYM + 'B')

        # Academic year should be the same as learning unit full [Inherit field]
        self.assertEqual(form_instance.instance.academic_year.id, self.learning_unit_year_full.academic_year.id)

    def _test_learning_container_model_form_instance(self, partim_form):
        """In this test, we ensure that the instance of learning container model form inherit
           from full learning container """
        form_instance = partim_form.form_instances[LearningContainerModelForm]
        self.assertEqual(form_instance.instance,
                         self.learning_unit_year_full.learning_container_year.learning_container)

    def _test_learning_container_year_model_form_instance(self, partim_form):
        """ In this test, we ensure that the instance of learning container year model form inherit
            from full learning container year """
        form_instance = partim_form.form_instances[LearningContainerYearModelForm]
        self.assertEqual(form_instance.instance,
                         self.learning_unit_year_full.learning_container_year)

    def _test_entity_container_model_formset_instance(self, partim_form):
        """ In this test, we ensure that the instance of learning container year model form inherit
            from full learning container year """
        formset_instance = partim_form.form_instances[EntityContainerFormset]
        self.assertEqual(formset_instance.instance,
                         self.learning_unit_year_full.learning_container_year)
        # Test expected instance
        expected_instance_form = [
            self.generated_container_year.requirement_entity_container_year,
            self.generated_container_year.allocation_entity_container_year,
            self.generated_container_year.additionnal_1_entity_container_year,
            self.generated_container_year.addtionnal_2_entity_container_year,
        ]
        for index, form in enumerate(formset_instance.forms):
            self.assertEqual(expected_instance_form[index], form.instance)


def get_valid_form_data(learning_unit_year_partim):
    acronym_splited = acronym_field.split_acronym(learning_unit_year_partim.acronym)
    post_data = {
        # Learning unit year data model form
        'acronym_2': acronym_splited[2],
        'subtype': learning_unit_year_partim.subtype,
        'specific_title': learning_unit_year_partim.specific_title,
        'specific_title_english': learning_unit_year_partim.specific_title_english,
        'credits': learning_unit_year_partim.credits,
        'session': learning_unit_year_partim.session,
        'quadrimester': learning_unit_year_partim.quadrimester,
        'status': learning_unit_year_partim.status,

        # Learning unit data model form
        'periodicity': learning_unit_year_partim.learning_unit.periodicity,
        'faculty_remark': learning_unit_year_partim.learning_unit.faculty_remark,
        'other_remark': learning_unit_year_partim.learning_unit.other_remark,
    }
    qdict = QueryDict('', mutable=True)
    qdict.update(post_data)
    return qdict
