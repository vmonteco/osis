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

from wheel.signatures.djbec import P

from base.forms.learning_unit.learning_unit_create_2 import FullForm, PartimForm, PARTIM_FORM_READ_ONLY_FIELD
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


def _instanciate_form(learning_unit_year_full, post_data=None, instance=None):
    person = PersonFactory()
    return PartimForm(post_data, person, learning_unit_year_full, instance=instance)

FULL_ACRONYM='LBIR1200'
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
    pass


def get_valid_form_data(learning_unit_year):
    return {
        # Learning unit data model form
        'periodicity': learning_unit_year.learning_unit.periodicity,
        'faculty_remark': learning_unit_year.learning_unit.faculty_remark,
        'other_remark': learning_unit_year.learning_unit.other_remark,
    }